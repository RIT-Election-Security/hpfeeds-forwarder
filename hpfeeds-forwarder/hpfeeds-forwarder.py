import os
import sys
import logging
import hpfeeds
from IPy import IP
from configparser import ConfigParser


LOG_FORMAT = '%(asctime)s - %(levelname)s - %(name)s[%(lineno)s][%(filename)s] - %(message)s'
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter(LOG_FORMAT))
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(handler)


def parse_ignore_cidr_option(cidrlist):
    """
    Given a comma-seperated list of CIDR addresses, split them and validate they're valid CIDR notation
    :param cidrlist: string representing a comma seperated list of CIDR addresses
    :return: a list containing IPy.IP objects representing the ignore_cidr addresses
    """
    cl = list()
    for c in cidrlist.split(','):
        try:
            s = c.strip(' ')
            i = IP(s)
            cl.append(i)
        except ValueError as e:
            logger.warning('Received invalid CIDR in ignore_cidr: {}'.format(e))
    return cl


def parse_config(config_file):
    if not os.path.isfile(config_file):
        sys.exit("Could not find configuration file: {0}".format(config_file))

    parser = ConfigParser()
    parser.read(config_file)

    config = dict()

    config['local_hpf_feeds'] = parser.get('local_hpfeeds', 'channels').split(',')
    config['local_hpf_ident'] = parser.get('local_hpfeeds', 'ident')
    config['local_hpf_secret'] = parser.get('local_hpfeeds', 'secret')
    config['local_hpf_port'] = parser.getint('local_hpfeeds', 'hp_port')
    config['local_hpf_host'] = parser.get('local_hpfeeds', 'hp_host')
    config['ignore_cidr'] = parser.get('local_hpfeeds', 'ignore_cidr')

    #config['remote_hpf_feeds'] = parser.get('remote_hpfeeds', 'channels').split(',')
    config['remote_hpf_ident'] = parser.get('remote_hpfeeds', 'ident')
    config['remote_hpf_secret'] = parser.get('remote_hpfeeds', 'secret')
    config['remote_hpf_port'] = parser.getint('remote_hpfeeds', 'hp_port')
    config['remote_hpf_host'] = parser.get('remote_hpfeeds', 'hp_host')

    logger.debug('Parsed config: {0}'.format(repr(config)))
    return config


def main():

    if len(sys.argv) < 2:
        logger.error('No config file found. Exiting')
        return 1

    if os.environ.get('DEBUG').upper() == 'TRUE':
        logger.setLevel(logging.DEBUG)

    config = parse_config(sys.argv[1])
    local_host = config['local_hpf_host']
    local_port = config['local_hpf_port']
    local_channels = [c for c in config['local_hpf_feeds']]
    local_ident = config['local_hpf_ident']
    local_secret = config['local_hpf_secret']

    remote_host = config['remote_hpf_host']
    remote_port = config['remote_hpf_port']
    remote_ident = config['remote_hpf_ident']
    remote_secret = config['remote_hpf_secret']

    ignore_cidr_l = parse_ignore_cidr_option(config['ignore_cidr'])

    try:
        logger.info('Initializing Local HPFeeds connection with {0}, {1}, {2}, {3}'.format(local_host,
                                                                                           local_port,
                                                                                           local_ident,
                                                                                           local_secret))
        local_hpc = hpfeeds.client.new(local_host, local_port, local_ident, local_secret)
    except hpfeeds.FeedException as e:
        logger.error('Experienced FeedException: {0}'.format(repr(e)))
        return 1

    try:
        logger.info('Initializing Local HPFeeds connection with {0}, {1}, {2}, {3}'.format(remote_host,
                                                                                           remote_port,
                                                                                           remote_ident,
                                                                                           remote_secret))
        remote_hpc = hpfeeds.client.new(remote_host, remote_port, remote_ident, remote_secret)
    except hpfeeds.FeedException as e:
        logger.error('Experienced FeedException: {0}'.format(repr(e)))
        return 1

    def on_message(identifier, channel, payload):
        logger.info('Received message: %s' % payload)
        remote_hpc.publish(channel, payload)

    def on_error(payload):
        logger.error('Error message from server: %s', payload)
        local_hpc.stop()

    local_hpc.subscribe(local_channels)
    try:
        local_hpc.run(on_message, on_error)
    except:
        pass
    finally:
        local_hpc.close()
        remote_hpc.close()


if __name__ == "__main__":
    main()
