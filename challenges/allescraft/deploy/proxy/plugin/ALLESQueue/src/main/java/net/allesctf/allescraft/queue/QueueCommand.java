package net.allesctf.allescraft.queue;

import net.md_5.bungee.api.ChatColor;
import net.md_5.bungee.api.CommandSender;
import net.md_5.bungee.api.chat.TextComponent;
import net.md_5.bungee.api.connection.ProxiedPlayer;

import java.util.Map;

public class QueueCommand extends PlayerTargetCommand {
	private final ALLESQueue instance;

	public QueueCommand(ALLESQueue instance) {
		super("queue", instance, 0);
		this.instance = instance;
	}

	@Override
	public void execute(CommandSender commandSender, String[] args, Map<Integer, ProxiedPlayer> targets) {
		if (!(commandSender instanceof ProxiedPlayer))
			return;

		TextComponent message = new TextComponent();
		message.setColor(ChatColor.RED);

		ProxiedPlayer player = (ProxiedPlayer) commandSender;
		if (!this.instance.staffPlayers.contains(player.getUniqueId())) {
			message.setText("Only staff may bypass the queue!");
			player.sendMessage(message);
			return;
		}

		if (args.length == 0) {
			this.instance.joinQueue.remove(player);
			this.instance.joinQueue.addFirst(player);

			message.setText("You have been placed at the top of the queue!");
			message.setColor(ChatColor.GREEN);
			message.setBold(true);
			player.sendMessage(message);
			this.instance.broadcastPluginMessage("status", "joinQueue", player.getUniqueId().toString());
			this.instance.consumeQueue();
			return;
		}

		ProxiedPlayer target = targets.get(0);
		if (target == null)
			return;

		TextComponent targetName = new TextComponent(target.getDisplayName());
		targetName.setColor(ChatColor.AQUA);

		this.instance.joinQueue.remove(target);
		this.instance.joinQueue.addFirst(target);

		message.setText("Player ");
		message.setColor(ChatColor.GREEN);
		message.addExtra(targetName);
		message.addExtra(" has been placed at the top of the queue!");
		player.sendMessage(message);

		this.instance.broadcastPluginMessage("status", "joinQueue", target.getUniqueId().toString());
		this.instance.consumeQueue();
	}
}
