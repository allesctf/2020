package net.allesctf.allescraft.queue;

import net.md_5.bungee.config.Configuration;
import net.md_5.bungee.config.ConfigurationProvider;
import net.md_5.bungee.config.JsonConfiguration;

import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;

public class PersistentConfiguration {
	private static final String CONFIG_FILE = "config.json";
	private final ALLESQueue instance;
	private Configuration configuration;

	public PersistentConfiguration(ALLESQueue instance) {
		this.instance = instance;
	}

	public void reload() throws IOException {
		if (!instance.getDataFolder().exists()) {
			//noinspection ResultOfMethodCallIgnored
			instance.getDataFolder().mkdir();
		}

		File configFile = new File(instance.getDataFolder(), CONFIG_FILE);
		if (!configFile.exists()) {
			InputStream defaultConfig = instance.getResourceAsStream("config.json");
			Files.copy(defaultConfig, configFile.toPath());
		}

		this.configuration = ConfigurationProvider.getProvider(JsonConfiguration.class).load(configFile);
	}

	public void save() throws IOException {
		ConfigurationProvider.getProvider(JsonConfiguration.class).save(
				configuration, new File(instance.getDataFolder(), CONFIG_FILE));
	}

	public Configuration get() {
		return configuration;
	}
}
