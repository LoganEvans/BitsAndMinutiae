import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
import pylab
import bintrees
import collections
import time
from pprint import pprint

from abc import ABCMeta, abstractmethod

class DistributionSimulation(object):
    __metaclass__ = ABCMeta
    def __init__(self):
        self.queue = collections.deque()
        self.value_tree = bintrees.rbtree.RBTree()

    @abstractmethod
    def _generate(self):
        pass

    def generate(self, n):
        for _ in xrange(n):
            value = self._generate()
            self.queue.append(value)
            self.value_tree[value] = self.value_tree.get(value, 0) + 1

    def remove(self, n):
        for _ in xrange(n):
            value = self.queue.popleft()
            self.value_tree[value] -= 1
            if not self.value_tree[value]:
                del self.value_tree[value]

    def count_interval(self, lower, upper):
        acc = 0
        for _, count in self.value_tree.item_slice(lower, upper):
            acc += count
        return acc

    def count(self):
        return len(self.queue)

    def __str__(self):
        return str(self.queue)

    def __iter__(self):
        for val in self.value_tree:
            yield val

    def add_histogram(self):
        n, bins, patches = pylab.hist(
                list(self), bins=100, normed=True, histtype='step')


class NormalSim(DistributionSimulation):
    def __init__(self, mu, sigma):
        DistributionSimulation.__init__(self)
        self.mu = mu
        self.sigma = sigma

    def _generate(self):
        return np.random.normal(self.mu, self.sigma)


class TruncatedNormalSim(DistributionSimulation):
    def __init__(self, mu, sigma, lower, upper):
        DistributionSimulation.__init__(self)
        self.mu = mu
        self.sigma = sigma
        self.lower = lower
        self.upper = upper

    def _generate(self):
        while True:
            val = np.random.normal(self.mu, self.sigma)
            if self.lower < val and val < self.upper:
                break
        return val


class UniformSim(DistributionSimulation):
    def __init__(self, lower, upper):
        DistributionSimulation.__init__(self)
        self.lower = lower
        self.upper = upper

    def _generate(self):
        return np.random.uniform(self.lower, self.upper)


def histogram_dists(dists):
    to_draw = []
    for _, dist in dists:
        for val in dist:
            to_draw.append(val)
    pylab.hist(to_draw, bins=100, normed=True, histtype='step')


def get_probs_cdf(target_dist, candidate_dists):
    n = reduce(lambda a, b: a[1].count() + b[1].count(), candidate_dists)
    intervals = []
    lower = float('-inf')
    cdf = 0
    for val in target_dist:
        upper = val
        count = 0
        for dist in candidate_dists:
            count += dist[1].count_interval(lower, upper)
        cdf += count / float(n)
        intervals.append([cdf, lower, upper])
        lower = upper
    intervals.append([1.0, upper, float('inf')])
    return intervals


def get_index_cdf(func, container, target_cdf):
    for i, blob in enumerate(container):
        if target_cdf < func(blob):
            return i
    return -1


class ProposalDists(object):
    def __init__(self, n, distributions):
        # Let's make it easy and set the priors as even...
        self.n = n
        self.dists = distributions
        self.dists[0].generate(
                math.ceil(self.n / float(len(distributions))))
        for dist in self.dists[1:]:
            dist.generate(math.floor(self.n / float(len(distributions))))
        # self.dists and self.cdf are parallel arrays.
        self._correct_distributions_cdf()

    def _correct_distributions_cdf(self):
        self.cdf = []
        cdf = 0
        for dist in self.dists:
            cdf += dist.count() / float(n)
            self.cdf.append(cdf)



def evict(probs_cdf, candidate_dists, n=1):
    for _ in xrange(n):
        slice_index = get_index_cdf(
                lambda x: x[0], probs_cdf, np.random.uniform(0, 1))
        lower, upper = probs_cdf[slice_index][1], probs_cdf[slice_index][2]
        evict_probs = []
        count_in_interval = 0
        to_add = 0
        for cdf, dist in candidate_dists:
            to_add += dist.count_interval(lower, upper)
            evict_probs.append(to_add)
        evict_probs = [val / float(to_add) for val in evict_probs]
        evict_choice = get_index_cdf(
                lambda x: x, evict_probs, np.random.uniform(0, 1))
        candidate_dists[evict_choice][1].remove(1)

    count = reduce(lambda x, y: x[1].count() + y[1].count(), candidate_dists)

    cdf = 0
    for idx in range(len(candidate_dists)):
        to_add = candidate_dists[idx][1].count() / float(count)
        cdf += to_add
        candidate_dists[idx][0] = cdf


def generate_from_priors(candidate_dists, n=1):
    for _ in xrange(n):
        choice = get_index_cdf(
                lambda x: x[0], candidate_dists, np.random.uniform(0, 1))
        candidate_dists[choice][1].generate(1)


if __name__ == '__main__':
    pylab.ion()

    target_dist = TruncatedNormalSim(0, 1, -5, 5)
    target_dist.generate(100)

    candidate_dists = [
            [0.9, UniformSim(-5, 5)],
            [1.0, TruncatedNormalSim(0, 1, -5, 5)]]

    n = 10000
    cdf = 0.0
    for dist in candidate_dists:
        dist[1].generate(int(n * (dist[0] - cdf)))
        cdf = dist[0]

    for _ in xrange(10):
        probs_cdf = get_probs_cdf(target_dist, candidate_dists)
        n = 2000
        evict(probs_cdf, candidate_dists, n=n)
        generate_from_priors(candidate_dists, n=n)
        histogram_dists(candidate_dists)
        pylab.draw()
    print candidate_dists
#   while True:
#       cur_time = time.time()
#       if cur_time - last_draw > epoch:
#           pylab.clf()
#           histogram_dists(candidate_dists)
#           pylab.draw()


#   time.sleep(1)



    '''
    n = UniformSim(-5, 5)
    n.generate(10000)
    n.add_histogram()
    pylab.draw()
    time.sleep(1)

    pylab.clf()

    o = TruncatedNormalSim(0, 1, -5, 5)
    o.generate(10000)
    o.add_histogram()
    pylab.draw()
    time.sleep(1)
    '''

