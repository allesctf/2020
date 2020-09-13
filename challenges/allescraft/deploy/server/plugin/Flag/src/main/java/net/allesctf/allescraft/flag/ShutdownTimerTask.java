package net.allesctf.allescraft.flag;

import org.spongepowered.api.Sponge;
import org.spongepowered.api.boss.BossBarColor;
import org.spongepowered.api.boss.BossBarColors;
import org.spongepowered.api.boss.BossBarOverlay;
import org.spongepowered.api.boss.BossBarOverlays;
import org.spongepowered.api.scheduler.Task;
import org.spongepowered.api.text.Text;
import org.spongepowered.api.text.format.TextColors;

import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.Consumer;

public class ShutdownTimerTask implements Consumer<Task> {
	private static final int START_TIME = 60 * 15;

	private final Flag instance;
	protected AtomicInteger seconds = new AtomicInteger(START_TIME + 1);

	public ShutdownTimerTask(Flag instance) {
		this.instance = instance;
	}

	@Override
	public void accept(Task task) {
		int seconds = this.seconds.decrementAndGet();

		if (seconds < -5) {
			task.cancel();
			Sponge.getServer().shutdown();
		} else if (seconds == 0) {
			Sponge.getChannelRegistrar()
					.getOrCreateRaw(this.instance, "BungeeCord")
					.sendToAll(buf -> buf.writeUTF("server").writeUTF("quit"));
		}

		if (this.instance.serverState != ServerState.FLAG_OBTAINED) {
			this.displayRemainingTime();
		}

		Sponge.getChannelRegistrar()
				.getOrCreateRaw(this.instance, "BungeeCord")
				.sendTo(this.instance.owningPlayer,
						buf -> buf.writeUTF("server").writeUTF("state").writeUTF(this.instance.serverState.toString())
								.writeUTF(String.valueOf(this.seconds)));
	}

	private void displayRemainingTime() {
		this.renderBossBar();

		int seconds = this.seconds.get();
		if (seconds <= 10 || seconds == 30 || seconds == 60 || seconds % (60 * 5) == 0) {
			Sponge.getServer().getBroadcastChannel().send(this, getRemainingTimeText());
		}
	}

	private void renderBossBar() {
		float percentage;
		BossBarColor color;
		BossBarOverlay overlay = BossBarOverlays.PROGRESS;

		int seconds = this.seconds.get();
		if (seconds <= 10) {
			color = BossBarColors.RED;
			percentage = seconds / 10f;
			overlay = BossBarOverlays.NOTCHED_10;
		} else if (seconds <= 60) {
			color = BossBarColors.BLUE;
			percentage = seconds / 60f;
		} else {
			color = BossBarColors.GREEN;
			percentage = seconds / (float) START_TIME;
		}

		percentage = Math.max(Math.min(percentage, 1f), 0f);
		this.instance.remainingTimeBar.setColor(color).setPercent(percentage).setOverlay(overlay).setVisible(true)
				.setName(this.getRemainingTimeText());
	}

	private Text getRemainingTimeText() {
		int seconds = this.seconds.get();
		if (seconds < 1) {
			return Text.of(TextColors.RED, "Time is up!");
		} else if (seconds == 1) {
			return Text.of(TextColors.DARK_RED, "Remaining Time: 1 second");
		} else if (seconds <= 10) {
			return Text.of(TextColors.DARK_RED, String.format("Remaining Time: %d seconds", seconds));
		} else if (seconds <= 30) {
			return Text.of(TextColors.GOLD, String.format("Remaining Time: %d seconds", seconds));
		} else if (seconds <= 60) {
			return Text.of(TextColors.YELLOW, String.format("Remaining Time: %d seconds", seconds));
		} else {
			int minutes = seconds / 60;
			int seconds_ = seconds % 60;

			String remainingTime = String.format("Remaining Time: %d %s %d %s",
					minutes, (minutes == 1) ? "minute" : "minutes",
					seconds_, (seconds_ == 1) ? "second" : "seconds");
			return Text.of(TextColors.DARK_GREEN, remainingTime);
		}
	}
}
