package net.allesctf.allescraft.queue;

import net.md_5.bungee.api.ChatColor;
import net.md_5.bungee.api.CommandSender;
import net.md_5.bungee.api.chat.TextComponent;
import net.md_5.bungee.api.config.ServerInfo;
import net.md_5.bungee.api.connection.ProxiedPlayer;

import java.util.Map;

public class LobbyCommand extends PlayerTargetCommand {
	private final ALLESQueue instance;

	public LobbyCommand(ALLESQueue instance) {
		super("lobby", instance, 0);
		this.instance = instance;
	}

	@Override
	public void execute(CommandSender commandSender, String[] args, Map<Integer, ProxiedPlayer> targets) {
		if (!(commandSender instanceof ProxiedPlayer))
			return;

		TextComponent message = new TextComponent();
		message.setColor(ChatColor.GREEN);

		ProxiedPlayer player = (ProxiedPlayer) commandSender;
		ServerInfo lobby = this.instance.getProxy().getServerInfo("lobby");

		if (lobby == null) {
			message.setText("Error: Could not get lobby server.");
			message.setColor(ChatColor.RED);
			player.sendMessage(message);
			return;
		}

		if (args.length == 0) {
			if (player.getServer().getInfo().equals(lobby)) {
				message.setText("You are already in the lobby!");
				player.sendMessage(message);
			} else {
				player.connect(lobby, (success, throwable) -> {
					if (success) {
						message.setText("You have been moved back into the lobby!");

						this.instance.usedServers.entrySet().stream()
								.filter(e -> e.getValue().equals(player))
								.forEach(e -> this.instance.usedServers.remove(e.getKey(), e.getValue()));
					} else {
						message.setText("Error whilst moving you back into the lobby.");
						message.setColor(ChatColor.RED);
					}

					player.sendMessage(message);
				});
			}

			return;
		}

		if (!this.instance.staffPlayers.contains(player.getUniqueId())) {
			message.setText("Only staff may forcefully move players into the lobby!");
			message.setColor(ChatColor.RED);
			player.sendMessage(message);
			return;
		}

		ProxiedPlayer target = targets.get(0);
		if (target == null)
			return;

		TextComponent targetName = new TextComponent(target.getDisplayName());
		targetName.setColor(ChatColor.AQUA);

		if (target.getServer().getInfo().equals(lobby)) {
			message.setText("Player ");
			message.addExtra(targetName);
			message.addExtra(" is already in the lobby!");
			player.sendMessage(message);
		} else {
			target.connect(lobby, (success, throwable) -> {
				if (success) {
					message.setText("You have been forcefully moved back into the lobby!");
					message.setColor(ChatColor.GOLD);
					target.sendMessage(message);

					message.setText("Successfully moved ");
					message.setColor(ChatColor.GREEN);
					message.addExtra(targetName);
					message.addExtra(" back into the lobby!");

					this.instance.usedServers.entrySet().stream()
							.filter(e -> e.getValue().equals(target))
							.forEach(e -> this.instance.usedServers.remove(e.getKey(), e.getValue()));
				} else {
					message.setText("Error whilst moving ");
					message.addExtra(targetName);
					message.addExtra(" back into the lobby.");
					message.setColor(ChatColor.RED);
				}

				player.sendMessage(message);
			});
		}
	}
}
