package net.allesctf.allescraft.queue;

import net.md_5.bungee.api.ChatColor;
import net.md_5.bungee.api.ChatMessageType;
import net.md_5.bungee.api.chat.TextComponent;
import net.md_5.bungee.api.config.ServerInfo;
import net.md_5.bungee.api.connection.ProxiedPlayer;
import net.md_5.bungee.api.event.PlayerDisconnectEvent;
import net.md_5.bungee.api.event.PluginMessageEvent;
import net.md_5.bungee.api.event.PostLoginEvent;
import net.md_5.bungee.api.plugin.Listener;
import net.md_5.bungee.api.plugin.Plugin;
import net.md_5.bungee.config.Configuration;
import net.md_5.bungee.event.EventHandler;
import net.md_5.bungee.protocol.packet.ScoreboardDisplay;
import net.md_5.bungee.protocol.packet.ScoreboardObjective;
import net.md_5.bungee.protocol.packet.ScoreboardScore;

import java.io.*;
import java.net.InetSocketAddress;
import java.time.Instant;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentLinkedDeque;
import java.util.concurrent.ConcurrentMap;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicReference;
import java.util.stream.Stream;

public class ALLESQueue extends Plugin implements Listener {
	protected final PersistentConfiguration configuration;

	protected final HashSet<UUID> staffPlayers = new HashSet<>();
	protected final HashSet<UUID> successfulPlayers = new HashSet<>();
	protected final AtomicReference<UUID> firstBlood = new AtomicReference<>();
	protected final HashSet<ProxiedPlayer> scoreboardPlayers = new HashSet<>();
	protected final ConcurrentLinkedDeque<ProxiedPlayer> joinQueue = new ConcurrentLinkedDeque<>();
	protected final ConcurrentMap<ServerInfo, Date> serverLastSeen = new ConcurrentHashMap<>();
	protected final ConcurrentMap<ServerInfo, ServerState> serverStates = new ConcurrentHashMap<>();
	protected final ConcurrentMap<ServerInfo, ProxiedPlayer> usedServers = new ConcurrentHashMap<>();

	public ALLESQueue() {
		this.configuration = new PersistentConfiguration(this);
	}

	@Override
	public void onEnable() {
		getProxy().getPluginManager().registerListener(this, this);

		registerServers();
		getProxy().getScheduler().schedule(this, this::updateScoreboards, 0, 1, TimeUnit.SECONDS);
		getProxy().getScheduler().schedule(this, this::updateServerStates, 0, 5, TimeUnit.SECONDS);

		try {
			this.configuration.reload();

			this.configuration.get().getStringList("staff").forEach(
					uuid -> staffPlayers.add(UUID.fromString(uuid)));
			this.configuration.get().getStringList("successfulPlayers").forEach(
					uuid -> successfulPlayers.add(UUID.fromString(uuid)));

			String firstBlood = this.configuration.get().getString("firstBlood", "");
			if (!firstBlood.isEmpty())
				this.firstBlood.set(UUID.fromString(firstBlood));
			else
				this.firstBlood.set(null);

			getProxy().getPluginManager().registerCommand(this, new FirstBloodCommand(this));
			getProxy().getPluginManager().registerCommand(this, new DeStaffCommand(this));
			getProxy().getPluginManager().registerCommand(this, new LobbyCommand(this));
			getProxy().getPluginManager().registerCommand(this, new QueueCommand(this));
			getProxy().getPluginManager().registerCommand(this, new StaffCommand(this));
			getProxy().getPluginManager().registerCommand(this, new StalkCommand(this));
		} catch (IOException e) {
			getLogger().warning("Could not load config, starting from clean state.");
			e.printStackTrace();
		}

		getLogger().info("ALLESQueue started");
	}

	@Override
	public void onDisable() {
		getProxy().getScheduler().cancel(this);
		getProxy().getPluginManager().unregisterListener(this);

		try {
			this.configuration.save();
		} catch (IOException e) {
			e.printStackTrace();
		}
		getLogger().info("ALLESQueue stopped");
	}

	@EventHandler
	public void onPluginMessageEvent(PluginMessageEvent ev) {
		if (!ev.getTag().equals("BungeeCord"))
			return;

		ev.setCancelled(true);
		DataInputStream in = new DataInputStream(new ByteArrayInputStream(ev.getData()));

		try {
			String channel = in.readUTF();
			String event = in.readUTF();
			String uuid;
			ProxiedPlayer player;

			switch (channel) {
				case "scoreboard":
					uuid = in.readUTF();
					player = getProxy().getPlayer(UUID.fromString(uuid));
					if (player == null)
						break;

					if (event.equals("join")) {
						this.scoreboardPlayers.add(player);
						this.updateScoreboard(player, this.getScoreboardServerStates());
					} else if (event.equals("leave")) {
						// Never remove the scoreboard for staff members
						if (this.staffPlayers.contains(player.getUniqueId()))
							break;

						this.scoreboardPlayers.remove(player);
						this.removeScoreboard(player);
					} else {
						getLogger().warning("Ignoring unknown scoreboard event: " + event);
					}
					break;

				case "queue":
					uuid = in.readUTF();
					player = getProxy().getPlayer(UUID.fromString(uuid));

					if (event.equals("join")) {
						if (!this.joinQueue.contains(player)) {
							this.joinQueue.addLast(player);

							TextComponent joinMessage = new TextComponent("Queue joined");
							joinMessage.setColor(ChatColor.DARK_GREEN);
							joinMessage.setBold(true);

							player.sendMessage(ChatMessageType.SYSTEM, joinMessage);
						}

						this.updateScoreboards();
						this.broadcastPluginMessage("status", "joinQueue", player.getUniqueId().toString());
						this.consumeQueue();
					} else if (event.equals("leave")) {
						this.joinQueue.remove(player);
						this.broadcastPluginMessage("status", "leaveQueue", player.getUniqueId().toString());
						this.updateScoreboards();
					} else {
						getLogger().warning("Ignoring unknown queue event: " + event);
					}
					break;

				case "server":
					Optional<ServerInfo> server = this.usedServers.keySet().stream().filter(
							s -> s.getSocketAddress().equals(ev.getSender().getSocketAddress())).findFirst();

					if (!server.isPresent()) {
						getLogger().warning("Received server event from invalid server...");
						break;
					}
					player = this.usedServers.get(server.get());

					switch (event) {
						case "flag":
							this.registerSuccess(player);
							break;

						case "quit":
							player.connect(getProxy().getServers().get("lobby"));
							this.usedServers.remove(server.get());
							break;

						case "state":
							String state = in.readUTF();
							String seconds = in.readUTF();
							ServerState serverState;

							try {
								serverState = new ServerState(state, Integer.parseInt(seconds));
							} catch (IllegalArgumentException e) {
								serverState = new ServerState(ServerState.State.UNKNOWN);
							}

							this.serverStates.put(server.get(), serverState);
							this.serverLastSeen.put(server.get(), Calendar.getInstance().getTime());
							break;

						default:
							getLogger().warning("Ignoring unknown server event: " + event);
							break;
					}
					break;

				case "admin":
					switch (event) {
						case "moveToLobby":
							uuid = in.readUTF();
							ProxiedPlayer otherPlayer = getProxy().getPlayer(UUID.fromString(uuid));

							otherPlayer.connect(getProxy().getServers().get("lobby"));
							break;

						case "getStaff":
							this.broadcastPluginMessage(Stream.concat(
									Stream.of("status", "staff"),
									this.staffPlayers.stream().map(UUID::toString)).toArray(String[]::new));
							break;

						case "getSuccessfulPlayers":
							this.broadcastPluginMessage(Stream.concat(
									Stream.of("status", "successfulPlayers"),
									this.successfulPlayers.stream().map(UUID::toString)).toArray(String[]::new));
							break;

						case "getFirstBlood":
							UUID firstBlood = this.firstBlood.get();
							if (firstBlood == null)
								this.broadcastPluginMessage("status", "firstBloodOld", "");
							else
								this.broadcastPluginMessage("status", "firstBloodOld", firstBlood.toString());
							break;

						default:
							getLogger().warning("Ignoring unknown server event: " + event);
							break;
					}
					break;

				default:
					getLogger().warning("Ignoring unknown channel: " + channel);
					ev.setCancelled(false);
					break;
			}
		} catch (IOException e) {
			e.printStackTrace();
		}
	}

	@EventHandler
	public void onPostLogin(PostLoginEvent ev) {
		this.scoreboardPlayers.add(ev.getPlayer());
		this.updateScoreboard(ev.getPlayer(), this.getScoreboardServerStates());
	}

	@EventHandler
	public void onPlayerDisconnect(PlayerDisconnectEvent ev) {
		ProxiedPlayer player = ev.getPlayer();

		this.joinQueue.remove(player);
		this.scoreboardPlayers.remove(player);
		this.broadcastPluginMessage("status", "leaveQueue", player.getUniqueId().toString());

		this.usedServers.entrySet().stream()
				.filter(s -> s.getValue().equals(player))
				.forEach(s -> this.usedServers.remove(s.getKey(), s.getValue()));
	}

	private void registerServers() {
		int n = Integer.parseInt(System.getenv("NUM_SERVERS"));
		int i = Integer.parseInt(System.getenv("IP_START_VALUE"));
		String template = System.getenv("IP_TEMPLATE");

		for (; i <= n; i++) {
			String ip = String.format(template, i);
			String name = String.format("S %02d", i);

			if (!getProxy().getServers().containsKey(name)) {
				ServerInfo serverInfo = getProxy().constructServerInfo(name, new InetSocketAddress(ip, 31337),
						"server", false);
				getProxy().getServers().put(name, serverInfo);
				this.serverLastSeen.put(serverInfo, Date.from(Instant.EPOCH));
				this.serverStates.put(serverInfo, new ServerState(ServerState.State.OFFLINE));
			}
		}
	}

	private void updateServerStates() {
		Calendar calendar = Calendar.getInstance();
		calendar.add(Calendar.SECOND, -3);
		this.serverLastSeen.entrySet().stream()
				.filter(s -> s.getValue().before(calendar.getTime()))
				.forEach(s ->
						s.getKey().ping((sp, ex) -> {
							if (ex != null) {
								this.serverStates.put(s.getKey(), new ServerState(ServerState.State.OFFLINE));
								return;
							}

							ServerState serverState;
							try {
								serverState = new ServerState(sp.getDescriptionComponent().toPlainText());
							} catch (IllegalArgumentException e) {
								serverState = new ServerState(ServerState.State.UNKNOWN);
							}

							this.serverStates.put(s.getKey(), serverState);
							this.serverLastSeen.put(s.getKey(), Calendar.getInstance().getTime());
						}));

		this.consumeQueue();
	}

	protected void consumeQueue() {
		this.serverStates.entrySet().stream()
				.filter(s -> s.getValue().getState().equals(ServerState.State.READY))
				.forEach(s -> usedServers.computeIfAbsent(s.getKey(), serverInfo -> {
					ProxiedPlayer player = this.joinQueue.pollFirst();
					if (player == null)
						return null;

					getLogger().info("Attempting to move " + player.getDisplayName() + " to " + serverInfo.getName());
					player.connect(serverInfo, (success, error) -> {
						if (!success) {
							this.usedServers.remove(serverInfo, player);
							this.joinQueue.addFirst(player);
							getLogger().info("Failure " + player.getDisplayName() + " -> " + serverInfo.getName());
						} else {
							getLogger().info("Success " + player.getDisplayName() + " -> " + serverInfo.getName());
							this.broadcastPluginMessage("status", "leaveQueue", player.getUniqueId().toString());
						}
					});

					return player;
				}));
	}

	private List<ScoreboardScore> getScoreboardServerStates() {
		List<ScoreboardScore> packets = new LinkedList<>();

		Iterator<Map.Entry<ServerInfo, ServerState>> it = this.serverStates.entrySet().iterator();
		for (int value = 12; value >= 0; value--) {
			if (!it.hasNext())
				break;

			Map.Entry<ServerInfo, ServerState> stateEntry = it.next();
			TextComponent text = new TextComponent(stateEntry.getKey().getName() + ": ");
			text.addExtra(stateEntry.getValue().getStatusMessage());

			packets.add(
					new ScoreboardScore(text.toLegacyText(), (byte) 0, "queue", value));
		}

		return packets;
	}

	private void updateScoreboards() {
		// Only calculate it once
		List<ScoreboardScore> serverStates = this.getScoreboardServerStates();
		this.scoreboardPlayers.forEach(p -> this.updateScoreboard(p, serverStates));
	}

	private void updateScoreboard(ProxiedPlayer player, List<ScoreboardScore> serverStates) {
		this.removeScoreboard(player);

		// Create the scoreboard
		player.unsafe().sendPacket(
				new ScoreboardObjective("queue", "ALLESQueue",
						ScoreboardObjective.HealthDisplay.INTEGER, (byte) 0));

		String queueSize = String.format("Queue size: %d", this.joinQueue.size());
		player.unsafe().sendPacket(
				new ScoreboardScore(queueSize, (byte) 0, "queue", 15));

		TextComponent queuePosition;

		if (!this.joinQueue.contains(player)) {
			queuePosition = new TextComponent("Not in queue");
			queuePosition.setColor(ChatColor.DARK_RED);
			queuePosition.setBold(true);
		} else {
			int position = 0;

			for (ProxiedPlayer p : this.joinQueue) {
				position++;

				if (p.equals(player))
					break;
			}

			queuePosition = new TextComponent(String.format("Queue position: %d", position));
			queuePosition.setColor(ChatColor.GREEN);
		}

		player.unsafe().sendPacket(
				new ScoreboardScore(queuePosition.toLegacyText(), (byte) 0, "queue", 14));
		player.unsafe().sendPacket(
				new ScoreboardScore("", (byte) 0, "queue", 13));

		// Send server states
		serverStates.forEach(p -> player.unsafe().sendPacket(p));
		player.unsafe().sendPacket(new ScoreboardDisplay((byte) 1, "queue"));
	}

	private void removeScoreboard(ProxiedPlayer player) {
		// Delete the scoreboard
		player.unsafe().sendPacket(
				new ScoreboardObjective("queue", "ALLESQueue",
						ScoreboardObjective.HealthDisplay.INTEGER, (byte) 1));
	}

	private void registerSuccess(ProxiedPlayer winner) {
		boolean newSuccess = this.successfulPlayers.add(winner.getUniqueId());

		if (this.firstBlood.compareAndSet(null, winner.getUniqueId())) {
			this.announceFirstBlood(winner);
		} else if (newSuccess) {
			this.announceFlag(winner);
		}

		this.writePersistentData();
	}

	protected void announceFirstBlood(ProxiedPlayer winner) {
		if (winner == null) {
			this.broadcastPluginMessage("status", "firstBloodOld", "");
			return;
		}

		TextComponent winningBroadcast = new TextComponent(winner.getDisplayName());
		TextComponent extra = new TextComponent(" just drew first blood! Congratulations!!");
		extra.setBold(true);
		extra.setColor(ChatColor.GOLD);
		winningBroadcast.setBold(true);
		winningBroadcast.setColor(ChatColor.AQUA);
		winningBroadcast.addExtra(extra);

		getProxy().broadcast(winningBroadcast);
		this.broadcastPluginMessage("status", "firstBlood", winner.getUniqueId().toString());
	}

	protected void announceFlag(ProxiedPlayer winner) {
		TextComponent winningBroadcast = new TextComponent(winner.getDisplayName());
		TextComponent extra = new TextComponent(" got the flag! Congratulations!");
		extra.setBold(true);
		extra.setColor(ChatColor.GREEN);
		winningBroadcast.setBold(true);
		winningBroadcast.setColor(ChatColor.AQUA);
		winningBroadcast.addExtra(extra);

		getProxy().broadcast(winningBroadcast);
		this.broadcastPluginMessage("status", "flag", winner.getUniqueId().toString());
	}

	protected void broadcastPluginMessage(String... data) {
		getProxy().getServers().forEach((n, serverInfo) -> {
			ByteArrayOutputStream bos = new ByteArrayOutputStream();
			DataOutputStream dos = new DataOutputStream(bos);
			try {
				for (String part : data)
					dos.writeUTF(part);

				serverInfo.sendData("BungeeCord", bos.toByteArray());
			} catch (IOException e) {
				e.printStackTrace();
			}
		});
	}

	protected void writePersistentData() {
		Configuration config = this.configuration.get();

		config.set("staff", this.staffPlayers.stream().map(UUID::toString).toArray());
		config.set("successfulPlayers", this.successfulPlayers.stream().map(UUID::toString).toArray());

		UUID firstBlood = this.firstBlood.get();
		config.set("firstBlood", (firstBlood == null) ? "" : firstBlood.toString());

		try {
			this.configuration.save();
		} catch (IOException e) {
			e.printStackTrace();
		}
	}
}
