package net.allesctf.allescraft.queue;

import net.md_5.bungee.api.ChatColor;
import net.md_5.bungee.api.chat.TextComponent;

public class ServerState {
	public enum State {
		UNKNOWN,
		OFFLINE,
		STARTING,
		READY,
		IN_USE,
		FLAG_OBTAINED,
		SHUTTING_DOWN;
	}

	private final State state;
	private final int secondsRemaining;

	public ServerState(State state) {
		this.state = state;
		this.secondsRemaining = 0;
	}

	public ServerState(String state) {
		this.state = State.valueOf(state);
		this.secondsRemaining = 0;
	}

	public ServerState(State state, int secondsRemaining) {
		this.state = state;
		this.secondsRemaining = secondsRemaining;
	}

	public ServerState(String state, int secondsRemaining) {
		this.state = State.valueOf(state);
		this.secondsRemaining = secondsRemaining;
	}

	public TextComponent getStatusMessage() {
		TextComponent component = new TextComponent(state.toString());

		switch (state) {
			case UNKNOWN:
			case OFFLINE:
				component.setColor(ChatColor.DARK_RED);
				break;

			case STARTING:
				component.setColor(ChatColor.AQUA);
				break;

			case READY:
				component.setColor(ChatColor.GREEN);
				break;

			case IN_USE:
				if (secondsRemaining < 0) {
					component.setText("STOPPING");
					component.setColor(ChatColor.AQUA);
					break;
				}

				int minutes = secondsRemaining / 60;
				int seconds = secondsRemaining % 60;
				component.setText(String.format("%02d:%02d", minutes, seconds));

				if (secondsRemaining <= 60) {
					component.setColor(ChatColor.GREEN);
				} else if (secondsRemaining <= 5 * 60) {
					component.setColor(ChatColor.YELLOW);
				} else if (secondsRemaining <= 10 * 60) {
					component.setColor(ChatColor.GOLD);
				} else {
					component.setColor(ChatColor.RED);
				}
				break;

			case FLAG_OBTAINED:
				component.setColor(ChatColor.GOLD);
				component.setText("FLAG");
				break;

			case SHUTTING_DOWN:
				component.setColor(ChatColor.DARK_PURPLE);
				component.setText("REBOOT");
				break;
		}

		return component;
	}

	public State getState() {
		return this.state;
	}

	public int getSecondsRemaining() {
		return this.secondsRemaining;
	}

	public boolean equals(ServerState other) {
		return this.state.equals(other.getState());
	}
}
