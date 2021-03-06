from collections import deque, Iterable
from abc import ABCMeta, abstractmethod
import bz2, pickle, os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

def load_cached_storage(cache_file, default_size=1000):
	if cache_file is not None and os.path.exists(cache_file):
		print("Loading cache: {0}".format(cache_file))
		with bz2.open(cache_file, "rb") as file:
			try:
				cache = pickle.load(file)
				return cache
			except pickle.PickleError and EOFError:
				return None
	return ThingCache(cache_size=default_size, file=cache_file)

class Cache(Iterable, metaclass=ABCMeta):
	def __init__(self, cache_file):
		self.cache_file = cache_file
	
	def __setitem__(self, key, value):
		pass
	
	@abstractmethod
	def __iter__(self):
		return None
	
	@abstractmethod
	def data(self):
		return None
	
	def save(self):
		os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
		if self.cache_file is not None:
			with bz2.open(self.cache_file, "wb") as file:
				pickle.dump(self, file)

class ThingCache(Cache):
	def __init__(self, cache_size=1000, file=None):
		super().__init__(file)
		
		self._post_ids = deque()
		self._post_ids_max = cache_size
	
	def _add_post_ids(self, post_ids):
		#Remove old posts
		new_len = len(self._post_ids) + len(post_ids)
		if new_len > self._post_ids_max:
			for n in range(0, new_len - self._post_ids_max):
				self._post_ids.popleft()
		#Add new posts
		for postID in post_ids:
			self._post_ids.append(postID)
		
		self.save()
	
	def get_diff(self, posts):
		if not posts:
			return list()
		posts = list(posts)
				
		#Get IDs not in the cache
		new_post_ids = [post.id for post in posts]
		new_post_ids = list(set(new_post_ids).difference(set(self._post_ids)))
				
		#Get new posts from IDs
		new_posts = []
		for postID in new_post_ids:
			for post in posts:
				if post.id == postID:
					new_posts.append(post)
		
		#Update cache
		self._add_post_ids(new_post_ids)
		
		return new_posts
	
	def data(self):
		return self._post_ids
	
	def __iter__(self):
		return self._post_ids.__iter__()
	
