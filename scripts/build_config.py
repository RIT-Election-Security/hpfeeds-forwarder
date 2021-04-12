import os
import sys
import uuid
import random
import logging
import configparser
from hpfeeds.add_user import create_user

LOG_FORMAT = '%(asctime)s - %(levelname)s - %(name)s[%(lineno)s][%(filename)s] - %(message)s'
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter(LOG_FORMAT))
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(handler)


def main():
    if os.environ.get('DEBUG').upper() == 'TRUE':
        logger.setLevel(logging.DEBUG)

    logger.info("Running build_config.py")

    MONGODB_HOST = os.environ.get("MONGODB_HOST", "mongodb")
    MONGODB_PORT = os.environ.get("MONGODB_PORT", "27017")
    LOCAL_HPFEEDS_HOST = os.environ.get("LOCAL_HPFEEDS_HOST", "hpfeeds3")
    LOCAL_HPFEEDS_PORT = os.environ.get("LOCAL_HPFEEDS_PORT", "10000")
    LOCAL_HPFEEDS_OWNER = os.environ.get("LOCAL_HPFEEDS_OWNER", "chn")
    LOCAL_HPFEEDS_IDENT = os.environ.get("LOCAL_HPFEEDS_IDENT", "")
    LOCAL_HPFEEDS_SECRET = os.environ.get("LOCAL_HPFEEDS_SECRET", "")
    LOCAL_HPFEEDS_CHANNELS = os.environ.get("LOCAL_HPFEEDS_CHANNELS",
                                            "amun.events,conpot.events,thug.events,beeswarm.hive,dionaea.capture,dionaea.connections,thug.files,beeswarm.feeder,cuckoo.analysis,kippo.sessions,cowrie.sessions,glastopf.events,glastopf.files,mwbinary.dionaea.sensorunique,snort.alerts,wordpot.events,p0f.events,suricata.events,shockpot.events,elastichoney.events,rdphoney.sessions,uhp.events,elasticpot.events,spylex.events")

    REMOTE_HPFEEDS_HOST = os.environ.get("REMOTE_HPFEEDS_HOST", "hpfeeds3")
    REMOTE_HPFEEDS_PORT = os.environ.get("REMOTE_HPFEEDS_PORT", "10000")
    REMOTE_HPFEEDS_OWNER = os.environ.get("REMOTE_HPFEEDS_OWNER", "chn")
    REMOTE_HPFEEDS_IDENT = os.environ.get("REMOTE_HPFEEDS_IDENT", "")
    REMOTE_HPFEEDS_SECRET = os.environ.get("REMOTE_HPFEEDS_SECRET", "")

    IGNORE_CIDR = os.environ.get("IGNORE_CIDR", "false")

    if LOCAL_HPFEEDS_IDENT:
        local_ident = LOCAL_HPFEEDS_IDENT
    else:
        local_ident = "hpfeeds-forwarder-" + str(random.randint(0, 32767))

    if LOCAL_HPFEEDS_SECRET:
        local_secret = REMOTE_HPFEEDS_SECRET
    else:
        local_secret = str(uuid.uuid4()).replace("-", "")

    config = configparser.ConfigParser()
    config.read("/opt/hpfeeds-forwarder.cfg.template")
    config['local_hpfeeds']['ident'] = local_ident
    config['local_hpfeeds']['secret'] = local_secret
    config['local_hpfeeds']['hp_host'] = LOCAL_HPFEEDS_HOST
    config['local_hpfeeds']['hp_port'] = LOCAL_HPFEEDS_PORT
    config['local_hpfeeds']['owner'] = LOCAL_HPFEEDS_OWNER
    config['local_hpfeeds']['channels'] = LOCAL_HPFEEDS_CHANNELS
    config['local_hpfeeds']['ignore_cidr'] = IGNORE_CIDR

    config['remote_hpfeeds']['ident'] = REMOTE_HPFEEDS_IDENT
    config['remote_hpfeeds']['secret'] = REMOTE_HPFEEDS_SECRET
    config['remote_hpfeeds']['hp_host'] = REMOTE_HPFEEDS_HOST
    config['remote_hpfeeds']['hp_port'] = REMOTE_HPFEEDS_PORT
    config['remote_hpfeeds']['owner'] = REMOTE_HPFEEDS_OWNER

    logger.info('Creating hpfeeds-bhr user in mongo...')
    logger.debug('Using values: host={}, port={}, owner={}, ident={}, secret={}, publish="", subscribe={}'.format(
        MONGODB_HOST, MONGODB_PORT, LOCAL_HPFEEDS_OWNER, local_ident, local_secret, LOCAL_HPFEEDS_CHANNELS))
    create_user(host=MONGODB_HOST, port=int(MONGODB_PORT), owner=LOCAL_HPFEEDS_OWNER,
                ident=local_ident, secret=local_secret, publish="", subscribe=LOCAL_HPFEEDS_CHANNELS)

    logger.info("Writing config...")

    with open("/opt/hpfeeds-forwarder.cfg", 'w') as config_file:
        config.write(config_file)
    sys.exit(0)


if __name__ == "__main__":
    main()
