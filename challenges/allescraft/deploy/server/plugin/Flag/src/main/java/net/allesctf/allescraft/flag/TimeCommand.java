package net.allesctf.allescraft.flag;

import org.checkerframework.checker.nullness.qual.NonNull;
import org.spongepowered.api.command.CommandResult;
import org.spongepowered.api.command.CommandSource;
import org.spongepowered.api.command.args.CommandContext;
import org.spongepowered.api.command.spec.CommandExecutor;

import java.util.Optional;

public class TimeCommand implements CommandExecutor {
	private final Flag instance;

	public TimeCommand(Flag instance) {
		this.instance = instance;
	}

	@Override
	@NonNull
	public CommandResult execute(@NonNull CommandSource src, @NonNull CommandContext args) {
		Optional<Object> seconds = args.getOne("seconds");
		if (seconds.isPresent() && seconds.get() instanceof Integer) {
			this.instance.shutdownTimerTask.seconds.set((Integer) seconds.get());
		}

		return CommandResult.success();
	}
}
