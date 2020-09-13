package net.allesctf.allescraft.flag;

import com.google.inject.Inject;
import org.slf4j.Logger;
import org.spongepowered.api.Platform;
import org.spongepowered.api.Sponge;
import org.spongepowered.api.boss.BossBarColors;
import org.spongepowered.api.boss.BossBarOverlays;
import org.spongepowered.api.boss.ServerBossBar;
import org.spongepowered.api.command.spec.CommandSpec;
import org.spongepowered.api.data.key.Keys;
import org.spongepowered.api.effect.sound.SoundCategories;
import org.spongepowered.api.effect.sound.SoundTypes;
import org.spongepowered.api.entity.living.player.Player;
import org.spongepowered.api.entity.living.player.gamemode.GameModes;
import org.spongepowered.api.event.Listener;
import org.spongepowered.api.event.game.state.GameStartedServerEvent;
import org.spongepowered.api.event.game.state.GameStoppingServerEvent;
import org.spongepowered.api.event.network.ClientConnectionEvent;
import org.spongepowered.api.event.server.ClientPingServerEvent;
import org.spongepowered.api.plugin.Plugin;
import org.spongepowered.api.scheduler.Task;
import org.spongepowered.api.text.Text;
import org.spongepowered.api.text.format.TextColors;
import org.spongepowered.api.text.title.Title;
import org.spongepowered.api.world.difficulty.Difficulties;
import org.spongepowered.api.world.storage.WorldProperties;

import java.util.UUID;
import java.util.concurrent.TimeUnit;

@Plugin(id = "flag", name = "Flag Plugin", version = "1.0", description = "Gives you the flag")
public class Flag {
	protected ServerState serverState = ServerState.STARTING;
	protected ServerBossBar remainingTimeBar;
	protected ShutdownTimerTask shutdownTimerTask;

	protected Player owningPlayer;

	@Inject
	private Logger logger;

	@Listener
	public void onServerStart(GameStartedServerEvent ev) {
		Sponge.getCommandManager().register(this,
				CommandSpec.builder().description(Text.of("Obtain the flag")).permission("*")
						.executor(new FlagCommand(this)).build(), "flag");

		/*
		Sponge.getCommandManager().register(this,
				CommandSpec.builder().description(Text.of("Shutdown time"))
						.arguments(GenericArguments.integer(Text.of("seconds")))
						.executor(new TimeCommand(this)).build(), "st");
		 */

		Sponge.getChannelRegistrar().getOrCreateRaw(this, "Bungeecord").addListener(Platform.Type.SERVER,
				(data, connection, side) -> {
					try {
						if (!data.readUTF().equals("status"))
							return;

						String type = data.readUTF();

						if (type.equals("firstBlood")) {
							Title firstBloodTitle = Title.of(Text.of(TextColors.RED, "⚠ FIRST BLOOD ⚠"));

							Sponge.getServer().getOnlinePlayers().forEach(player -> {
								player.sendTitle(firstBloodTitle);
								player.playSound(SoundTypes.ENTITY_ENDERDRAGON_DEATH, SoundCategories.MASTER,
										player.getLocation().getPosition(), 1.0, 1.0);
							});
						} else if (type.equals("flag")) {
							Sponge.getServer().getOnlinePlayers().forEach(player ->
									player.playSound(SoundTypes.ENTITY_ENDERDRAGON_DEATH, SoundCategories.MASTER,
											player.getLocation().getPosition(), 1.0, 1.0));
						}
					} catch (Exception e) {
						e.printStackTrace();
					}
				});

		this.remainingTimeBar = ServerBossBar.builder().visible(false).name(Text.of("Placeholder"))
				.color(BossBarColors.GREEN).percent(1f).overlay(BossBarOverlays.PROGRESS).build();
		this.shutdownTimerTask = new ShutdownTimerTask(this);

		logger.info("Server started, marking as ready");
		this.serverState = ServerState.READY;
	}

	@Listener
	public void onServerStopping(GameStoppingServerEvent ev) {
		this.serverState = ServerState.SHUTTING_DOWN;
	}

	@Listener
	public void onPlayerJoin(ClientConnectionEvent.Join ev) {
		this.remainingTimeBar.addPlayer(ev.getTargetEntity());

		if (this.serverState == ServerState.READY) {
			this.serverState = ServerState.IN_USE;

			Task.builder().execute(this.shutdownTimerTask).interval(1, TimeUnit.SECONDS)
					.name("Countdown").submit(this);

			Sponge.getServer().getWorlds().forEach(w -> {
				WorldProperties properties = w.getProperties();

				// Reset time and weather, additionally clear hostile mobs
				properties.setWorldTime(0);
				properties.setRaining(false);
				properties.setThundering(false);
				properties.setGameMode(GameModes.SPECTATOR);
				properties.setDifficulty(Difficulties.PEACEFUL);
				properties.setDifficulty(Difficulties.NORMAL);
			});

			// Set owning player, so admins can join afterwards
			this.owningPlayer = ev.getTargetEntity();
			this.owningPlayer.offer(Keys.GAME_MODE, GameModes.SURVIVAL);
		} else {
			// Admin joined
			ev.setMessageCancelled(true);

			Player player = ev.getTargetEntity();
			Sponge.getServer().getOnlinePlayers().forEach(p -> {
				if (p.equals(player))
					return;

				p.getTabList().removeEntry(player.getUniqueId());
			});
			player.offer(Keys.VANISH, true);
			player.offer(Keys.VANISH_IGNORES_COLLISION, true);
			player.offer(Keys.VANISH_PREVENTS_TARGETING, true);
			player.offer(Keys.GAME_MODE, GameModes.SPECTATOR);
		}

		Sponge.getChannelRegistrar().getOrCreateRaw(this, "BungeeCord").sendTo(ev.getTargetEntity(),
				buf -> buf.writeUTF("scoreboard").writeUTF("leave")
						.writeUTF(ev.getTargetEntity().getUniqueId().toString()));
	}

	@Listener
	public void onPlayerDisconnect(ClientConnectionEvent.Disconnect ev) {
		// Shutdown the server if the owning player exits
		// We need this check in order for ALLES! admins to be able to join and leave
		// We are always watching :) Build us something nice ;)
		if (ev.getTargetEntity().equals(this.owningPlayer)) {
			this.serverState = ServerState.SHUTTING_DOWN;

			Sponge.getServer().getOnlinePlayers().forEach(player -> {
				if (player.equals(this.owningPlayer))
					return;

				Sponge.getChannelRegistrar().getOrCreateRaw(this, "BungeeCord")
						.sendTo(player, buf -> buf.writeUTF("admin").writeUTF("moveToLobby")
								.writeUTF(player.getUniqueId().toString()));
			});

			Task.builder().execute(() -> Sponge.getServer().shutdown()).delay(5, TimeUnit.SECONDS)
					.name("Shutdown").submit(this);
		} else {
			ev.setMessageCancelled(true);
		}
	}

	@Listener
	public void onServerPing(ClientPingServerEvent ev) {
		ev.getResponse().setDescription(Text.of(this.serverState.toString()));
	}
}
