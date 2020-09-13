package net.allesctf.allescraft.queue;

import net.md_5.bungee.api.ChatColor;
import net.md_5.bungee.api.CommandSender;
import net.md_5.bungee.api.chat.TextComponent;
import net.md_5.bungee.api.connection.ProxiedPlayer;
import net.md_5.bungee.api.plugin.Command;

import java.util.HashMap;
import java.util.Map;
import java.util.Optional;

public abstract class PlayerTargetCommand extends Command {
	private final ALLESQueue instance;
	private final int[] positions;

	public PlayerTargetCommand(String name, ALLESQueue instance, int... positions) {
		super(name);
		this.instance = instance;
		this.positions = positions;
	}

	public void execute(CommandSender commandSender, String[] args) {
		Map<Integer, ProxiedPlayer> results = new HashMap<>();

		for (Integer position : positions) {
			if (args.length <= position)
				continue;

			Optional<ProxiedPlayer> target = this.instance.getProxy().getPlayers().stream()
					.filter(p -> p.getDisplayName().equalsIgnoreCase(args[position])).findFirst();

			if (target.isPresent()) {
				results.put(position, target.get());
			} else {
				TextComponent notFoundMessage = new TextComponent("Could not find player with name ");
				TextComponent userName = new TextComponent();

				userName.setText(args[position]);
				userName.setColor(ChatColor.AQUA);

				notFoundMessage.addExtra(userName);
				notFoundMessage.addExtra("!");
				notFoundMessage.setColor(ChatColor.RED);
				commandSender.sendMessage(notFoundMessage);
			}
		}

		this.execute(commandSender, args, results);
	}

	public abstract void execute(CommandSender commandSender, String[] args, Map<Integer, ProxiedPlayer> targets);
}
