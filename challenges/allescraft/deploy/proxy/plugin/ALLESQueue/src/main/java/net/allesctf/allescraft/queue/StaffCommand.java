package net.allesctf.allescraft.queue;

import net.md_5.bungee.api.ChatColor;
import net.md_5.bungee.api.CommandSender;
import net.md_5.bungee.api.chat.TextComponent;
import net.md_5.bungee.api.config.ServerInfo;
import net.md_5.bungee.api.connection.ProxiedPlayer;

import java.util.Map;

public class StaffCommand extends PlayerTargetCommand {
	private final ALLESQueue instance;

	public StaffCommand(ALLESQueue instance) {
		super("staff", instance, 0);
		this.instance = instance;
	}

	@Override
	public void execute(CommandSender commandSender, String[] args, Map<Integer, ProxiedPlayer> targets) {
		if ((commandSender instanceof ProxiedPlayer) &&
				!this.instance.staffPlayers.contains(((ProxiedPlayer) commandSender).getUniqueId())) {
			TextComponent message = new TextComponent("Only staff may edit the staff list!");
			message.setColor(ChatColor.RED);
			commandSender.sendMessage(message);
			return;
		}

		if (args.length == 0) {
			TextComponent message = new TextComponent("You need to provide a player to be added to the staff list!");
			message.setColor(ChatColor.RED);
			commandSender.sendMessage(message);
			return;
		}

		ProxiedPlayer target = targets.get(0);
		if (target == null)
			return;

		TextComponent targetName = new TextComponent(target.getDisplayName());
		targetName.setColor(ChatColor.AQUA);

		if (this.instance.staffPlayers.add(target.getUniqueId())) {
			TextComponent message = new TextComponent("You have just been promoted to staff!");
			message.setColor(ChatColor.GOLD);
			target.sendMessage(message);

			message.setText("Successfully added ");
			message.addExtra(targetName);
			message.addExtra(" to the staff list!");
			message.setColor(ChatColor.GREEN);
			commandSender.sendMessage(message);

			this.instance.broadcastPluginMessage("status", "addStaff", target.getUniqueId().toString());
			this.instance.writePersistentData();
		} else {
			TextComponent message = new TextComponent("Player ");
			message.addExtra(targetName);
			message.addExtra(" is already staff.");
			message.setColor(ChatColor.RED);
			commandSender.sendMessage(message);
		}
	}
}
