package net.allesctf.allescraft.queue;

import net.md_5.bungee.api.ChatColor;
import net.md_5.bungee.api.CommandSender;
import net.md_5.bungee.api.chat.TextComponent;
import net.md_5.bungee.api.config.ServerInfo;
import net.md_5.bungee.api.connection.ProxiedPlayer;
import net.md_5.bungee.api.plugin.Command;

import java.util.Map;
import java.util.Optional;

public class FirstBloodCommand extends Command {
	private final ALLESQueue instance;

	public FirstBloodCommand(ALLESQueue instance) {
		super("firstblood");
		this.instance = instance;
	}

	@Override
	public void execute(CommandSender commandSender, String[] args) {
		if ((commandSender instanceof ProxiedPlayer) &&
				!this.instance.staffPlayers.contains(((ProxiedPlayer) commandSender).getUniqueId())) {
			TextComponent message = new TextComponent("Only staff may edit the first blood!");
			message.setColor(ChatColor.RED);
			commandSender.sendMessage(message);
			return;
		}

		if (args.length == 0){
			TextComponent usage = new TextComponent("Usage: /firstblood [-/playername] (- clears the first blood)");
			usage.setColor(ChatColor.WHITE);
			commandSender.sendMessage(usage);
			return;
		}

		if (args[0].equals("-")) {
			this.instance.firstBlood.set(null);
			this.instance.announceFirstBlood(null);

			TextComponent message = new TextComponent("First blood successfully cleared!");
			message.setColor(ChatColor.GREEN);
			commandSender.sendMessage(message);
		} else {
			Optional<ProxiedPlayer> target = this.instance.getProxy().getPlayers().stream()
					.filter(p -> p.getDisplayName().equalsIgnoreCase(args[0])).findFirst();

			TextComponent targetName = new TextComponent();
			targetName.setColor(ChatColor.AQUA);

			if (target.isPresent()) {
				this.instance.firstBlood.set(target.get().getUniqueId());
				this.instance.announceFirstBlood(target.get());

				targetName.setText(target.get().getDisplayName());

				TextComponent message = new TextComponent("First blood successfully awarded to ");
				message.setColor(ChatColor.GREEN);
				message.addExtra(targetName);
				message.addExtra("!");

				commandSender.sendMessage(message);
			} else {
				targetName.setText(args[0]);

				TextComponent message = new TextComponent("No player with name ");
				message.setColor(ChatColor.RED);
				message.addExtra(targetName);
				message.addExtra(".");

				commandSender.sendMessage(message);
			}
		}

		this.instance.writePersistentData();
	}
}
