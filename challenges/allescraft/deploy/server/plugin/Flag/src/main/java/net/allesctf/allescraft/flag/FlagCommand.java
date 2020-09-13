package net.allesctf.allescraft.flag;

import org.checkerframework.checker.nullness.qual.NonNull;
import org.spongepowered.api.Sponge;
import org.spongepowered.api.boss.BossBarColors;
import org.spongepowered.api.boss.BossBarOverlays;
import org.spongepowered.api.command.CommandResult;
import org.spongepowered.api.command.CommandSource;
import org.spongepowered.api.command.args.CommandContext;
import org.spongepowered.api.command.spec.CommandExecutor;
import org.spongepowered.api.entity.living.player.Player;
import org.spongepowered.api.text.Text;
import org.spongepowered.api.text.format.TextColor;
import org.spongepowered.api.text.format.TextColors;
import org.spongepowered.api.text.format.TextStyles;
import org.spongepowered.api.text.title.Title;

import java.io.BufferedReader;
import java.io.InputStreamReader;

public class FlagCommand implements CommandExecutor {
	private final static TextColor[] TEXT_COLOURS = {TextColors.DARK_RED, TextColors.RED, TextColors.GOLD,
			TextColors.YELLOW, TextColors.DARK_GREEN, TextColors.GREEN, TextColors.AQUA, TextColors.DARK_AQUA,
			TextColors.DARK_BLUE, TextColors.BLUE, TextColors.LIGHT_PURPLE, TextColors.DARK_PURPLE};

	private final Flag instance;

	public FlagCommand(Flag instance) {
		this.instance = instance;
	}

	private Text getFlagContent() {
		try {
			final BufferedReader flagReader = new BufferedReader(
					new InputStreamReader(Runtime.getRuntime().exec("/getflag").getInputStream()));
			String flag = flagReader.readLine();

			Text.Builder builder = Text.builder();
			int i = 0;
			for (char c : flag.toCharArray()) {
				builder.append(Text.builder(c).color(TEXT_COLOURS[i % TEXT_COLOURS.length]).build());
				i += 1;
			}

			return builder.build();
		} catch (Exception e) {
			e.printStackTrace();
			return Text.builder("ERROR, contact admin").color(TextColors.DARK_RED).build();
		}
	}

	@Override
	@NonNull
	public CommandResult execute(@NonNull CommandSource src, @NonNull CommandContext args) {
		if (!(src instanceof Player))
			return CommandResult.success();

		// Prevent admins from accidentally leaking the flag - we should probably much rather
		// prevent trigger happy admins from stalking, but whatever
		Player player = (Player) src;
		if (!player.equals(this.instance.owningPlayer)) {
			player.sendMessage(Text.of(
					TextColors.RED, TextStyles.BOLD, "You don't own this server! Flag not retrieved."));

			return CommandResult.success();
		}

		try {
			player.sendMessage(
					Text.builder("Here is your flag: ").style(TextStyles.BOLD)
							.append(this.getFlagContent()).build());

			player.sendTitle(Title.of(Text.of(TextColors.GREEN, TextStyles.BOLD, "Congratulations!")));

			Sponge.getChannelRegistrar()
					.getOrCreateRaw(this.instance, "BungeeCord")
					.sendTo(player, buf -> buf.writeUTF("server").writeUTF("flag"));
		} catch (Exception e) {
			e.printStackTrace();
		}

		if (this.instance.serverState == ServerState.IN_USE) {
			this.instance.serverState = ServerState.FLAG_OBTAINED;
			this.instance.remainingTimeBar.setName(this.getFlagContent())
					.setOverlay(BossBarOverlays.PROGRESS).setColor(BossBarColors.GREEN).setPercent(1f);
			this.instance.shutdownTimerTask.seconds.set(10);
		}

		return CommandResult.success();
	}
}
