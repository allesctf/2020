package net.allesctf.allescraft.queue;

import net.md_5.bungee.api.ChatColor;
import net.md_5.bungee.api.CommandSender;
import net.md_5.bungee.api.chat.TextComponent;
import net.md_5.bungee.api.connection.ProxiedPlayer;
import net.md_5.bungee.api.connection.Server;

import java.util.Map;

public class StalkCommand extends PlayerTargetCommand {
	private final ALLESQueue instance;

	public StalkCommand(ALLESQueue instance) {
		super("stalk", instance, 0);
		this.instance = instance;
	}

	@Override
	public void execute(CommandSender commandSender, String[] args, Map<Integer, ProxiedPlayer> targets) {
		if (!(commandSender instanceof ProxiedPlayer))
			return;

		TextComponent message = new TextComponent();
		message.setColor(ChatColor.RED);

		ProxiedPlayer player = (ProxiedPlayer) commandSender;

		if (args.length == 0) {
			message.setText("Server states:");
			message.setColor(ChatColor.GREEN);
			player.sendMessage(message);

			message.setColor(ChatColor.WHITE);
			this.instance.serverStates.forEach((serverInfo, serverState) -> {
				TextComponent serverStateText = new TextComponent(serverInfo.getName() + ": ");
				serverStateText.setColor(ChatColor.WHITE);

				if (serverState.getState().equals(ServerState.State.IN_USE)) {
					TextComponent userName = new TextComponent();
					ProxiedPlayer user = this.instance.usedServers.get(serverInfo);

					if (user == null) {
						userName.setText("Unknown");
						userName.setColor(ChatColor.RED);
					} else {
						userName.setText(user.getDisplayName());
						userName.setColor(ChatColor.AQUA);
					}

					serverStateText.addExtra(userName);
					serverStateText.addExtra(" - ");
				}

				serverStateText.addExtra(serverState.getStatusMessage());
				player.sendMessage(serverStateText);
			});

			return;
		}

		if (!this.instance.staffPlayers.contains(player.getUniqueId())) {
			message.setText("Only staff may stalk!");
			player.sendMessage(message);
			return;
		}

		ProxiedPlayer target = targets.get(0);
		if (target == null)
			return;

		TextComponent targetName = new TextComponent(target.getDisplayName());
		targetName.setColor(ChatColor.AQUA);

		Server targetServer = target.getServer();
		if (targetServer.equals(player.getServer())) {
			message.setText("You are already on the same server!");
			message.setColor(ChatColor.GREEN);
			player.sendMessage(message);
			return;
		}

		player.connect(targetServer.getInfo(), (success, throwable) -> {
			if (!success) {
				message.setText("Error moving you to the same server.");
			} else {
				message.setText("You were moved to the same server as ");
				message.addExtra(targetName);
				message.addExtra("!");
				message.setColor(ChatColor.GREEN);
			}

			player.sendMessage(message);
		});
	}
}
