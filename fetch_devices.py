"""
Module to find devices having SSH connection.

This module finds all devices connected in the same network and is ssh enabled and accessable.
"""
import socket
import ipaddress
import logging
from typing import Optional
import yaml
import paramiko
from  munch import DefaultMunch

class DeviceAccess():
    """
    Class responsible to fetching and displaying ssh enabled and accessable devices ip address.
    """
    def __init__(self):
        config_file_path= 'config.yaml'
        self.config= self.load_config(config_file_path)
        self.logger= None
        self.configure_logging()
        self.set_log_level(self.config.log_level)

    def set_log_level(self, configured_log_level: str = 'INFO') -> None:
        """
        Set the log level based on the configured log level.

        :param configured_log_level (str): The desired log level as a string. Defaults to 'INFO'
            if not specified or invalid. Valid values: 'INFO', 'DEBUG', 'WARN' or 'WARNING', 'ERROR'

        :return: None
        """
        log_level = logging.INFO
        if configured_log_level:
            configured_level = configured_log_level.upper()
            if configured_level in ['INFO', 'DEBUG', 'WARN', 'WARNING', 'ERROR']:
                log_level = getattr(logging, configured_level)
                self.logger.info(f"Setting log level to {configured_level}")
            else:
                self.logger.warning(f"Invalid log level '{configured_level}'. Setting log level to INFO.")
        else:
            self.logger.info("Setting default log level INFO")

        self.logger.setLevel(log_level)

    def configure_logging(self):
        """
        Configure logging and formatting.
        """
        # Configure logging
        self.logger = logging.getLogger(__name__)
        # self.logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        self.logger.addHandler(stream_handler)

    def load_config(self, file_path)-> Optional[DefaultMunch]:
        """
        Load config from yaml file.
        :param file_path: path to config yaml file.
        :return: configuration munch object
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as config_file:
                config_yaml = yaml.safe_load(config_file)
                config = DefaultMunch.fromDict(config_yaml)
            return config
        except FileNotFoundError:
            print(f"Config file not found: {file_path}")
            return None
        except Exception as error:
            print(f"Error while loading config: {error}")
            return None

    def check_ssh_access(self, ip, username, password):
        """
        Method to check ssh access to a privided ip address.
        """
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(ip, port=22, username=username, password=password, timeout=2)
            ssh.close()
            return True
        except (paramiko.AuthenticationException, paramiko.SSHException, socket.error) as e:
            # self.logger.error(f"Error: {e}")
            return False

    def find_devices_in_network(self):
        """
        Fetch all devices connected in a network and are accessible through ssh.
        """
        self.logger.debug("This process can take upto 5 minutes.".center(100, '*'))
        network_ip= f"{self.config.network_ip}/24"
        username= self.config.username
        password= self.config.password
        network = ipaddress.IPv4Network(network_ip)  # Change this to your network
        devices_with_ssh_access = []
        for ip in network.hosts():
            ip = str(ip)
            if self.check_ssh_access(ip, username, password):
                self.logger.debug(f"Fount access with ip address: {ip}")
                devices_with_ssh_access.append(ip)
        return devices_with_ssh_access

    def display_found_devices(self, devices_with_ssh):
        """
        Method to display ip addresses.
        """
        self.logger.info("Devices with SSH access:")
        if not devices_with_ssh:
            self.logger.error("Empty list")
            return
        for device in devices_with_ssh:
            self.logger.info(device)

def main():
    """
    Main function to derive module.
    """
    device= DeviceAccess()
    devices_with_ssh = device.find_devices_in_network()
    device.display_found_devices(devices_with_ssh)

if __name__ == "__main__":
    main()
