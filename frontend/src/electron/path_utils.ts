import { Settings } from "./settings";

export function validateSettings(json: unknown): json is Settings {
  const errors: string[] = [];

  if (typeof json !== "object" || json === null) {
    console.error("Validation failed: Input is not an object.");
    return false;
  }

  const settings = json as Partial<Settings>;

  if (typeof settings.serial_port !== "string") {
    errors.push("serial_port should be a string");
  }
  if (typeof settings.baud_rate !== "number") {
    errors.push("baud_rate should be a number");
  }
  if (typeof settings.pwm_step_size !== "number") {
    errors.push("pwm_step_size should be a number");
  }
  if (typeof settings.command_delay !== "number") {
    errors.push("command_delay should be a number");
  }
  if (typeof settings.serial_connection_wait !== "number") {
    errors.push("serial_connection_wait should be a number");
  }
  if (typeof settings.csv_file !== "string") {
    errors.push("csv_file should be a string");
  }

  if (errors.length > 0) {
    console.error("Validation errors:", errors.join(", "));
    return false;
  }

  return true;
}
