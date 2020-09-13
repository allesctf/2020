package net.allesctf.allescraft.lobby;

import com.flowpowered.math.vector.Vector3d;
import com.google.common.collect.ImmutableMap;
import com.google.inject.Inject;
import org.slf4j.Logger;
import org.spongepowered.api.Platform;
import org.spongepowered.api.Sponge;
import org.spongepowered.api.block.BlockTypes;
import org.spongepowered.api.data.key.Keys;
import org.spongepowered.api.effect.sound.SoundCategories;
import org.spongepowered.api.effect.sound.SoundTypes;
import org.spongepowered.api.entity.living.player.Player;
import org.spongepowered.api.entity.living.player.gamemode.GameModes;
import org.spongepowered.api.event.Listener;
import org.spongepowered.api.event.block.InteractBlockEvent;
import org.spongepowered.api.event.entity.CollideEntityEvent;
import org.spongepowered.api.event.entity.DamageEntityEvent;
import org.spongepowered.api.event.filter.cause.First;
import org.spongepowered.api.event.game.state.GameStartedServerEvent;
import org.spongepowered.api.event.item.inventory.DropItemEvent;
import org.spongepowered.api.event.network.ClientConnectionEvent;
import org.spongepowered.api.plugin.Plugin;
import org.spongepowered.api.scheduler.Task;
import org.spongepowered.api.scoreboard.CollisionRules;
import org.spongepowered.api.scoreboard.Scoreboard;
import org.spongepowered.api.scoreboard.Team;
import org.spongepowered.api.scoreboard.Visibilities;
import org.spongepowered.api.text.Text;
import org.spongepowered.api.text.format.TextColors;
import org.spongepowered.api.text.format.TextStyles;
import org.spongepowered.api.text.title.Title;
import org.spongepowered.api.world.Location;
import org.spongepowered.api.world.World;
import org.spongepowered.api.world.difficulty.Difficulties;

import java.util.*;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicReference;

@Plugin(id = "lobby", name = "Lobby Plugin", version = "1.0", description = "Does lobby things")
public class Lobby {
	private static final Map<UserStates, Vector3d[]> SPAWNPOINTS = ImmutableMap.of(
			UserStates.PROOF_OF_WORK, new Vector3d[]{
					new Vector3d(5.5, 60, -40.5),
					new Vector3d(90, 90, 0)
			},
			UserStates.QUEUE, new Vector3d[]{new Vector3d(5.5, 4, -40.5)},
			UserStates.STAFF, new Vector3d[]{new Vector3d(2.5, 64, -41.5)}
	);

	private static final Map<UserStates, Team> TEAMS = ImmutableMap.of(
			UserStates.PROOF_OF_WORK, Team.builder().name(UserStates.PROOF_OF_WORK.toString())
					.displayName(Text.of(TextColors.GRAY, "Proof of work"))
					.deathTextVisibility(Visibilities.NEVER).nameTagVisibility(Visibilities.ALWAYS)
					.prefix(Text.of(TextColors.GRAY, "[PoW] ", TextColors.WHITE))
					.allowFriendlyFire(false).collisionRule(CollisionRules.NEVER).build(),
			UserStates.QUEUE, Team.builder().name(UserStates.QUEUE.toString())
					.displayName(Text.of(TextColors.BLUE, "Queue"))
					.deathTextVisibility(Visibilities.NEVER).nameTagVisibility(Visibilities.ALWAYS)
					.prefix(Text.of(TextColors.BLUE, "[Queue] "))
					.allowFriendlyFire(false).collisionRule(CollisionRules.NEVER).build(),
			UserStates.FLAG, Team.builder().name(UserStates.FLAG.toString())
					.displayName(Text.of(TextColors.GOLD, "Flag"))
					.deathTextVisibility(Visibilities.NEVER).nameTagVisibility(Visibilities.ALWAYS)
					.prefix(Text.of(TextColors.GOLD, "[Flag] "))
					.allowFriendlyFire(false).collisionRule(CollisionRules.NEVER).build(),
			UserStates.FIRST_BLOOD, Team.builder().name(UserStates.FIRST_BLOOD.toString())
					.displayName(Text.of(TextColors.RED, "First Blood"))
					.deathTextVisibility(Visibilities.NEVER).nameTagVisibility(Visibilities.ALWAYS)
					.prefix(Text.of(TextColors.RED, "[First Blood] "))
					.allowFriendlyFire(false).collisionRule(CollisionRules.NEVER).build(),
			UserStates.STAFF, Team.builder().name(UserStates.STAFF.toString())
					.displayName(Text.of(TextColors.GREEN, "Staff"))
					.deathTextVisibility(Visibilities.NEVER).nameTagVisibility(Visibilities.ALWAYS)
					.prefix(Text.of(TextColors.GREEN, "[Staff] ")).canSeeFriendlyInvisibles(true)
					.allowFriendlyFire(false).collisionRule(CollisionRules.NEVER).build()
	);
	private static final Scoreboard SCOREBOARD = Scoreboard.builder().teams(new ArrayList<>(TEAMS.values())).build();


	private final Set<UUID> staff = new HashSet<>();
	private final Set<UUID> joinQueue = new HashSet<>();
	private final Set<UUID> successfulPlayers = new HashSet<>();
	private final AtomicReference<UUID> firstBlood = new AtomicReference<>(null);

	private enum Synchronisations {
		STAFF,
		JOIN_QUEUE,
		FIRST_BLOOD,
		SUCCESSFUL_PLAYERS
	}

	private final Set<Synchronisations> synchronisations = new HashSet<>();

	@Inject
	private Logger logger;

	@Listener
	public void onServerStart(GameStartedServerEvent ev) {
		Sponge.getChannelRegistrar().getOrCreateRaw(this, "BungeeCord").addListener(Platform.Type.SERVER,
				(data, connection, side) -> {
					try {
						// Ignore all non-status updates
						if (!data.readUTF().equals("status"))
							return;

						String status = data.readUTF();
						UUID uuid;

						switch (status) {
							case "joinQueue":
								uuid = UUID.fromString(data.readUTF());
								this.joinQueue.add(uuid);

								Sponge.getServer().getPlayer(uuid).ifPresent(player -> {
									this.assignPlayerTeam(player);
									logger.info("{} moved into queue team", player.getName());
									Task.builder().execute(task -> respawn(player, false)).submit(this);
								});
								break;

							case "leaveQueue":
								uuid = UUID.fromString(data.readUTF());
								this.joinQueue.remove(uuid);

								Sponge.getServer().getPlayer(uuid).ifPresent(player -> {
									this.assignPlayerTeam(player);
									logger.info("{} removed from queue team", player.getName());
									Task.builder().execute(task -> respawn(player, false)).submit(this);
								});
								break;

							case "firstBlood":
								// Handle whatever the proxy can't
								Title firstBloodTitle = Title.of(Text.of(TextColors.RED, "⚠ FIRST BLOOD ⚠"));
								Sponge.getServer().getOnlinePlayers().forEach(player -> {
									player.sendTitle(firstBloodTitle);
									player.playSound(SoundTypes.ENTITY_ENDERDRAGON_DEATH, SoundCategories.MASTER,
											player.getLocation().getPosition(), 1.0, 1.0);
								});

								/* Falls through */
							case "firstBloodOld":
								String uuidString = data.readUTF();
								UUID oldFirstBlood;

								if (uuidString.isEmpty()) {
									oldFirstBlood = this.firstBlood.getAndSet(null);
								} else {
									uuid = UUID.fromString(uuidString);
									oldFirstBlood = this.firstBlood.getAndSet(uuid);
									this.successfulPlayers.add(uuid);

									Sponge.getServer().getPlayer(uuid).ifPresent(this::assignPlayerTeam);
								}

								Sponge.getServer().getPlayer(oldFirstBlood).ifPresent(this::assignPlayerTeam);
								logger.info("Stored new first blood: {}", this.firstBlood.get());
								this.synchronisations.add(Synchronisations.FIRST_BLOOD);
								break;

							case "flag":
								// Handle whatever the proxy can't
								uuid = UUID.fromString(data.readUTF());
								this.successfulPlayers.add(uuid);

								Sponge.getServer().getPlayer(uuid).ifPresent(player -> {
									this.assignPlayerTeam(player);
									Task.builder().execute(task -> respawn(player, false)).submit(this);
								});

								Sponge.getServer().getOnlinePlayers().forEach(player ->
										player.playSound(SoundTypes.ENTITY_ENDERDRAGON_DEATH, SoundCategories.MASTER,
												player.getLocation().getPosition(), 1.0, 1.0));
								break;

							case "staff":
								this.staff.clear();

								while (data.available() > 0)
									this.staff.add(UUID.fromString(data.readUTF()));

								Sponge.getServer().getOnlinePlayers().forEach(player -> {
									if (this.staff.contains(player.getUniqueId())) {
										this.assignPlayerTeam(player);
										player.offer(Keys.GAME_MODE, GameModes.SPECTATOR);

										Sponge.getServer().getOnlinePlayers().stream()
												.filter(p -> !this.staff.contains(p.getUniqueId()))
												.forEach(otherPlayer -> otherPlayer.getTabList().removeEntry(player.getUniqueId()));
									}
								});

								logger.info("Received staff list from server");
								this.synchronisations.add(Synchronisations.STAFF);
								break;

							case "successfulPlayers":
								this.successfulPlayers.clear();

								while (data.available() > 0)
									this.successfulPlayers.add(UUID.fromString(data.readUTF()));

								Sponge.getServer().getOnlinePlayers().forEach(this::assignPlayerTeam);
								logger.info("Received successful players list from server");
								this.synchronisations.add(Synchronisations.SUCCESSFUL_PLAYERS);
								break;

							case "addStaff":
								uuid = UUID.fromString(data.readUTF());
								this.staff.add(uuid);

								Sponge.getServer().getPlayer(uuid).ifPresent(player -> {
									this.assignPlayerTeam(player);
									player.offer(Keys.GAME_MODE, GameModes.SPECTATOR);

									Sponge.getServer().getOnlinePlayers().stream()
											.filter(p -> !this.staff.contains(p.getUniqueId()))
											.forEach(otherPlayer -> otherPlayer.getTabList().removeEntry(player.getUniqueId()));
								});
								break;

							case "removeStaff":
								uuid = UUID.fromString(data.readUTF());
								this.staff.remove(uuid);

								Sponge.getServer().getPlayer(uuid).ifPresent(player -> {
									this.assignPlayerTeam(player);
									player.offer(Keys.GAME_MODE, GameModes.ADVENTURE);

									Sponge.getServer().getOnlinePlayers().stream()
											.filter(p -> this.staff.contains(p.getUniqueId()))
											.forEach(otherPlayer -> player.getTabList().removeEntry(otherPlayer.getUniqueId()));
									this.respawn(player, false);
								});
								break;

							default:
								logger.info("Ignoring status update of unknown type {}", status);
								break;
						}
					} catch (Exception e) {
						e.printStackTrace();
					}
				});

		Sponge.getServer().getWorlds().forEach(world -> {
			world.getProperties().setGameMode(GameModes.SPECTATOR);
			world.getProperties().setDifficulty(Difficulties.PEACEFUL);
			world.getProperties().setPVPEnabled(false);
		});

		logger.info("Server started.");
	}

	@Listener
	public void onBlock(InteractBlockEvent.Secondary ev) {
		if (ev.getTargetBlock().getState().getType().equals(BlockTypes.STONE_BUTTON)) {
			Optional<Player> player = ev.getCause().first(Player.class);
			player.ifPresent(value -> this.sendToBungeeCord(value,
					"queue", "join", value.getUniqueId().toString()));
		}
	}

	@Listener
	public void onPlayerJoin(ClientConnectionEvent.Join ev) {
		Player player = ev.getTargetEntity();
		Team playerTeam = this.assignPlayerTeam(player);

		if (playerTeam.equals(TEAMS.get(UserStates.STAFF))) {
			Sponge.getServer().getOnlinePlayers().stream().filter(p -> !p.equals(player)).forEach(otherPlayer -> {
				if (!this.staff.contains(otherPlayer.getUniqueId()))
					otherPlayer.getTabList().removeEntry(player.getUniqueId());
			});
		} else {
			Sponge.getServer().getOnlinePlayers().forEach(otherPlayer -> {
				if (this.staff.contains(otherPlayer.getUniqueId()))
					player.getTabList().removeEntry(otherPlayer.getUniqueId());
			});

			player.offer(Keys.GAME_MODE, GameModes.ADVENTURE);
		}

		player.setScoreboard(SCOREBOARD);

		logger.info("{} joined with team {}", player.getName(), playerTeam.getDisplayName().toPlain());

		this.respawn(player, false);

		if (!this.synchronisations.contains(Synchronisations.STAFF)) {
			this.sendToBungeeCord(player, "admin", "getStaff");
			logger.info("Requested staff list with player {} as carrier", player.getName());
		}

		if (!this.synchronisations.contains(Synchronisations.JOIN_QUEUE)) {
			this.sendToBungeeCord(player, "admin", "getQueue");
			logger.info("Requested queue with player {} as carrier", player.getName());
		}

		if (!this.synchronisations.contains(Synchronisations.FIRST_BLOOD)) {
			this.sendToBungeeCord(player, "admin", "getFirstBlood");
			logger.info("Requested first blood with player {} as carrier", player.getName());
		}

		if (!this.synchronisations.contains(Synchronisations.SUCCESSFUL_PLAYERS)) {
			this.sendToBungeeCord(player, "admin", "getSuccessfulPlayers");
			logger.info("Requested successful players list with player {} as carrier", player.getName());
		}

		ev.setMessageCancelled(true);
		this.sendToBungeeCord(player, "scoreboard", "join", player.getUniqueId().toString());
	}

	@Listener
	public void onPlayerLeave(ClientConnectionEvent.Disconnect ev) {
		ev.setMessageCancelled(true);
	}

	@Listener
	public void onCollide(CollideEntityEvent ev) {
		ev.setCancelled(true);
	}

	@Listener
	public void playerDropItem(DropItemEvent ev) {
		ev.setCancelled(true);
	}

	@Listener
	public void onDamage(DamageEntityEvent ev, @First Player player) {
		AtomicBoolean tryHarder = new AtomicBoolean(true);

		SCOREBOARD.getMemberTeam(player.getTeamRepresentation()).ifPresent(team -> {
			if (team.equals(TEAMS.get(UserStates.STAFF)) || team.equals(TEAMS.get(UserStates.QUEUE)))
				tryHarder.set(false);
		});

		ev.setCancelled(true);
		respawn(player, tryHarder.get());
	}

	private Team assignPlayerTeam(Player player) {
		// Revoke all teams
		TEAMS.values().forEach(team -> team.removeMember(player.getTeamRepresentation()));

		UUID firstBlood = this.firstBlood.get();
		Team team;

		if (this.staff.contains(player.getUniqueId())) {
			team = TEAMS.get(UserStates.STAFF);
		} else if (this.joinQueue.contains(player.getUniqueId())) {
			team = TEAMS.get(UserStates.QUEUE);
		} else if (firstBlood != null && firstBlood.equals(player.getUniqueId())) {
			team = TEAMS.get(UserStates.FIRST_BLOOD);
		} else if (this.successfulPlayers.contains(player.getUniqueId())) {
			team = TEAMS.get(UserStates.FLAG);
		} else {
			team = TEAMS.get(UserStates.PROOF_OF_WORK);
		}

		team.addMember(player.getTeamRepresentation());
		return team;
	}

	private void respawn(Player player, boolean tryHarder) {
		if (this.staff.contains(player.getUniqueId()))
			return;

		Optional<Team> team = SCOREBOARD.getMemberTeam(player.getTeamRepresentation());
		Vector3d[] respawnLocation = null;

		if (team.isPresent())
			respawnLocation = SPAWNPOINTS.get(UserStates.valueOf(team.get().getName()));

		if (respawnLocation == null)
			respawnLocation = SPAWNPOINTS.get(UserStates.PROOF_OF_WORK);

		Location<World> playerLocation = player.getLocation().setPosition(respawnLocation[0]);

		if (respawnLocation.length >= 2)
			player.setLocationAndRotationSafely(playerLocation, respawnLocation[1]);
		else
			player.setLocationSafely(playerLocation);

		player.offer(Keys.HEALTH, 20.0);
		player.offer(Keys.FOOD_LEVEL, 20);
		player.offer(Keys.SATURATION, 20.0);

		if (tryHarder)
			player.sendTitle(Title.of(Text.of(TextStyles.BOLD, TextColors.DARK_PURPLE, "Try harder")));
	}

	private void sendToBungeeCord(Player carrier, String... data) {
		Sponge.getChannelRegistrar().getOrCreateRaw(this, "BungeeCord")
				.sendTo(carrier, buf -> {
					for (String message : data)
						buf.writeUTF(message);
				});
	}
}
