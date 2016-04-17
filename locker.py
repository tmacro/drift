#Etcd locking and coordination goes here
import etcd
import config
import utils
import logging
moduleLogger = logging.getLogger('locker')

etcdClient = etcd.Client(host=config.ETCD_HOST, port=2379)

def TakeLock(path):
	sanPath = utils.stripAllSpecial(path)
	lock = etcd.Lock(etcdClient, config.ETCD_ROOT[1:] + sanPath)
	moduleLogger.debug('Aquiring lock for %s'%path)
	lock.acquire(blocking=False, timeout=10)
	if lock.is_acquired:
		return lock

	return False
