export interface Settings {
    serial_port: string;
    baud_rate: number;
    pwm_step_size: number;
    command_delay: number;
    serial_connection_wait: number;
    csv_file: string;
}
 
export const defaultSettings: Settings = {
    serial_port: "COM12",
    baud_rate: 115200,
    pwm_step_size: 20,
    command_delay: 1500,
    serial_connection_wait: 3,
    csv_file: "test_log.csv",
};