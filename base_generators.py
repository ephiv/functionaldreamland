import random
import math
import heapq
import bisect
import itertools
import collections
import re


def clj(value):
    if value is None:
        return "nil"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        if isinstance(value, float):
            if math.isinf(value):
                return "1e309" if value > 0 else "-1e309"
            if math.isnan(value):
                return "0.0"
        return str(value)
    if isinstance(value, str):
        return '"' + value.replace('"', '\\"') + '"'
    if isinstance(value, (list, tuple)):
        return "[" + " ".join(clj(v) for v in value) + "]"
    if isinstance(value, set):
        return "[" + " ".join(clj(v) for v in sorted(value)) + "]"
    raise TypeError(f"Unsupported type: {type(value)}")


def rand_list(n, lo, hi):
    return [random.randint(lo, hi) for _ in range(n)]


def rand_string(n, alphabet="abcdefghijklmnopqrstuvwxyz"):
    return "".join(random.choice(alphabet) for _ in range(n))


class TreeNode:
    __slots__ = ("val", "left", "right")

    def __init__(self, val, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def list_to_tree(arr):
    if not arr:
        return None
    nodes = [None if v is None else TreeNode(v) for v in arr]
    for i, node in enumerate(nodes):
        if node is None:
            continue
        li = 2 * i + 1
        ri = 2 * i + 2
        if li < len(nodes):
            node.left = nodes[li]
        if ri < len(nodes):
            node.right = nodes[ri]
    return nodes[0]


def tree_to_list(root):
    if not root:
        return []
    out = []
    q = collections.deque([root])
    while q:
        node = q.popleft()
        if node is None:
            out.append(None)
            continue
        out.append(node.val)
        q.append(node.left)
        q.append(node.right)
    while out and out[-1] is None:
        out.pop()
    return out


GENERATORS = {}


def register(key):
    def deco(fn):
        GENERATORS[key] = fn
        return fn
    return deco


def generate_case(key):
    if key not in GENERATORS:
        raise ValueError(f"Unknown generator key: {key}")
    return GENERATORS[key]()


@register("two_sum")
def gen_two_sum():
    n = random.randint(4, 12)
    nums = rand_list(n, -20, 20)
    i, j = random.sample(range(n), 2)
    target = nums[i] + nums[j]
    return {"args": clj([nums, target]), "expected": clj([i, j])}


@register("two_sum_ii")
def gen_two_sum_ii():
    n = random.randint(4, 12)
    nums = sorted(rand_list(n, -20, 20))
    i, j = random.sample(range(n), 2)
    if i > j:
        i, j = j, i
    target = nums[i] + nums[j]
    return {"args": clj([nums, target]), "expected": clj([i + 1, j + 1])}


@register("three_sum")
def gen_three_sum():
    n = random.randint(6, 12)
    nums = rand_list(n, -10, 10)
    nums.sort()
    res = set()
    for i in range(n):
        if i > 0 and nums[i] == nums[i - 1]:
            continue
        l, r = i + 1, n - 1
        while l < r:
            s = nums[i] + nums[l] + nums[r]
            if s == 0:
                res.add((nums[i], nums[l], nums[r]))
                l += 1
                r -= 1
                while l < r and nums[l] == nums[l - 1]:
                    l += 1
                while l < r and nums[r] == nums[r + 1]:
                    r -= 1
            elif s < 0:
                l += 1
            else:
                r -= 1
    out = [list(t) for t in sorted(res)]
    return {"args": clj([nums]), "expected": clj(out)}


@register("four_sum")
def gen_four_sum():
    n = random.randint(6, 10)
    nums = rand_list(n, -10, 10)
    target = random.randint(-5, 5)
    nums.sort()
    res = set()
    for a in range(n):
        if a > 0 and nums[a] == nums[a - 1]:
            continue
        for b in range(a + 1, n):
            if b > a + 1 and nums[b] == nums[b - 1]:
                continue
            l, r = b + 1, n - 1
            while l < r:
                s = nums[a] + nums[b] + nums[l] + nums[r]
                if s == target:
                    res.add((nums[a], nums[b], nums[l], nums[r]))
                    l += 1
                    r -= 1
                    while l < r and nums[l] == nums[l - 1]:
                        l += 1
                    while l < r and nums[r] == nums[r + 1]:
                        r -= 1
                elif s < target:
                    l += 1
                else:
                    r -= 1
    out = [list(t) for t in sorted(res)]
    return {"args": clj([nums, target]), "expected": clj(out)}


@register("subarray_sum_k")
def gen_subarray_sum_k():
    n = random.randint(6, 14)
    nums = rand_list(n, -5, 5)
    k = random.randint(-5, 5)
    count = 0
    for i in range(n):
        s = 0
        for j in range(i, n):
            s += nums[j]
            if s == k:
                count += 1
    return {"args": clj([nums, k]), "expected": clj(count)}


@register("subarray_product_lt_k")
def gen_subarray_product_lt_k():
    n = random.randint(5, 10)
    nums = [random.randint(1, 10) for _ in range(n)]
    k = random.randint(2, 40)
    count = 0
    for i in range(n):
        prod = 1
        for j in range(i, n):
            prod *= nums[j]
            if prod < k:
                count += 1
    return {"args": clj([nums, k]), "expected": clj(count)}


@register("max_subarray")
def gen_max_subarray():
    n = random.randint(5, 12)
    nums = rand_list(n, -10, 10)
    best = nums[0]
    cur = nums[0]
    for x in nums[1:]:
        cur = max(x, cur + x)
        best = max(best, cur)
    return {"args": clj([nums]), "expected": clj(best)}


@register("max_product_subarray")
def gen_max_product_subarray():
    n = random.randint(5, 10)
    nums = rand_list(n, -5, 5)
    best = nums[0]
    cur_min = nums[0]
    cur_max = nums[0]
    for x in nums[1:]:
        if x < 0:
            cur_min, cur_max = cur_max, cur_min
        cur_max = max(x, cur_max * x)
        cur_min = min(x, cur_min * x)
        best = max(best, cur_max)
    return {"args": clj([nums]), "expected": clj(best)}


@register("min_size_subarray_sum")
def gen_min_size_subarray_sum():
    n = random.randint(5, 12)
    nums = [random.randint(1, 10) for _ in range(n)]
    target = random.randint(10, 30)
    best = math.inf
    for i in range(n):
        s = 0
        for j in range(i, n):
            s += nums[j]
            if s >= target:
                best = min(best, j - i + 1)
                break
    res = 0 if best == math.inf else best
    return {"args": clj([target, nums]), "expected": clj(res)}


@register("longest_consecutive")
def gen_longest_consecutive():
    n = random.randint(6, 12)
    nums = rand_list(n, -10, 10)
    s = set(nums)
    best = 0
    for x in s:
        if x - 1 not in s:
            cur = 1
            y = x + 1
            while y in s:
                cur += 1
                y += 1
            best = max(best, cur)
    return {"args": clj([nums]), "expected": clj(best)}


@register("min_rotated")
def gen_min_rotated():
    n = random.randint(5, 10)
    nums = sorted(rand_list(n, -20, 20))
    k = random.randint(0, n - 1)
    rot = nums[k:] + nums[:k]
    return {"args": clj([rot]), "expected": clj(min(rot))}


@register("search_rotated")
def gen_search_rotated():
    n = random.randint(5, 10)
    nums = sorted(set(rand_list(n, -20, 20)))
    k = random.randint(0, len(nums) - 1)
    rot = nums[k:] + nums[:k]
    target = random.choice(nums + [999])
    idx = rot.index(target) if target in rot else -1
    return {"args": clj([rot, target]), "expected": clj(idx)}


@register("find_peak")
def gen_find_peak():
    n = random.randint(5, 10)
    nums = rand_list(n, -20, 20)
    def is_peak(i):
        left = nums[i - 1] if i > 0 else -math.inf
        right = nums[i + 1] if i < n - 1 else -math.inf
        return nums[i] > left and nums[i] > right
    peaks = [i for i in range(n) if is_peak(i)]
    idx = peaks[0]
    return {"args": clj([nums]), "expected": clj(idx)}


@register("kth_largest")
def gen_kth_largest():
    n = random.randint(6, 12)
    nums = rand_list(n, -20, 20)
    k = random.randint(1, n)
    expected = sorted(nums, reverse=True)[k - 1]
    return {"args": clj([nums, k]), "expected": clj(expected)}


@register("top_k_frequent")
def gen_top_k_frequent():
    n = random.randint(6, 12)
    nums = rand_list(n, -5, 5)
    k = random.randint(1, min(5, len(set(nums))))
    cnt = collections.Counter(nums)
    expected = [x for x, _ in cnt.most_common(k)]
    return {"args": clj([nums, k]), "expected": clj(expected)}


@register("sort_colors")
def gen_sort_colors():
    n = random.randint(6, 12)
    nums = [random.randint(0, 2) for _ in range(n)]
    expected = sorted(nums)
    return {"args": clj([nums]), "expected": clj(expected)}


@register("merge_intervals")
def gen_merge_intervals():
    n = random.randint(4, 8)
    intervals = []
    for _ in range(n):
        a = random.randint(0, 10)
        b = random.randint(a, a + 5)
        intervals.append([a, b])
    intervals.sort()
    merged = []
    for s, e in intervals:
        if not merged or s > merged[-1][1]:
            merged.append([s, e])
        else:
            merged[-1][1] = max(merged[-1][1], e)
    return {"args": clj([intervals]), "expected": clj(merged)}


@register("insert_interval")
def gen_insert_interval():
    n = random.randint(3, 6)
    intervals = []
    cur = 0
    for _ in range(n):
        start = cur + random.randint(0, 2)
        end = start + random.randint(0, 3)
        intervals.append([start, end])
        cur = end + 1
    new_start = random.randint(0, cur)
    new_end = new_start + random.randint(0, 3)
    new_interval = [new_start, new_end]
    all_ints = sorted(intervals + [new_interval])
    merged = []
    for s, e in all_ints:
        if not merged or s > merged[-1][1]:
            merged.append([s, e])
        else:
            merged[-1][1] = max(merged[-1][1], e)
    return {"args": clj([intervals, new_interval]), "expected": clj(merged)}


@register("non_overlapping_intervals")
def gen_non_overlapping_intervals():
    n = random.randint(4, 8)
    intervals = []
    for _ in range(n):
        a = random.randint(0, 10)
        b = random.randint(a + 1, a + 5)
        intervals.append([a, b])
    intervals.sort(key=lambda x: x[1])
    remove = 0
    end = -math.inf
    for s, e in intervals:
        if s >= end:
            end = e
        else:
            remove += 1
    return {"args": clj([intervals]), "expected": clj(remove)}


@register("interval_intersections")
def gen_interval_intersections():
    def make_list():
        cur = 0
        out = []
        for _ in range(random.randint(3, 6)):
            start = cur + random.randint(0, 2)
            end = start + random.randint(0, 3)
            out.append([start, end])
            cur = end + random.randint(0, 2)
        return out
    A = make_list()
    B = make_list()
    i = j = 0
    res = []
    while i < len(A) and j < len(B):
        s = max(A[i][0], B[j][0])
        e = min(A[i][1], B[j][1])
        if s <= e:
            res.append([s, e])
        if A[i][1] < B[j][1]:
            i += 1
        else:
            j += 1
    return {"args": clj([A, B]), "expected": clj(res)}


@register("meeting_rooms_ii")
def gen_meeting_rooms_ii():
    n = random.randint(4, 8)
    intervals = []
    for _ in range(n):
        start = random.randint(0, 10)
        end = start + random.randint(1, 5)
        intervals.append([start, end])
    intervals.sort()
    heap = []
    for s, e in intervals:
        if heap and heap[0] <= s:
            heapq.heapreplace(heap, e)
        else:
            heapq.heappush(heap, e)
    return {"args": clj([intervals]), "expected": clj(len(heap))}

@register("sliding_window_max")
def gen_sliding_window_max():
    n = random.randint(6, 12)
    nums = rand_list(n, -10, 10)
    k = random.randint(2, min(5, n))
    res = [max(nums[i:i + k]) for i in range(n - k + 1)]
    return {"args": clj([nums, k]), "expected": clj(res)}


@register("trapping_rain")
def gen_trapping_rain():
    n = random.randint(6, 12)
    height = [random.randint(0, 6) for _ in range(n)]
    left = [0] * n
    right = [0] * n
    m = 0
    for i in range(n):
        m = max(m, height[i])
        left[i] = m
    m = 0
    for i in range(n - 1, -1, -1):
        m = max(m, height[i])
        right[i] = m
    water = sum(min(left[i], right[i]) - height[i] for i in range(n))
    return {"args": clj([height]), "expected": clj(water)}


@register("container_most_water")
def gen_container_most_water():
    n = random.randint(6, 12)
    height = [random.randint(1, 10) for _ in range(n)]
    best = 0
    l, r = 0, n - 1
    while l < r:
        best = max(best, (r - l) * min(height[l], height[r]))
        if height[l] < height[r]:
            l += 1
        else:
            r -= 1
    return {"args": clj([height]), "expected": clj(best)}


@register("daily_temperatures")
def gen_daily_temperatures():
    n = random.randint(6, 12)
    temps = [random.randint(50, 90) for _ in range(n)]
    res = [0] * n
    stack = []
    for i, t in enumerate(temps):
        while stack and temps[stack[-1]] < t:
            j = stack.pop()
            res[j] = i - j
        stack.append(i)
    return {"args": clj([temps]), "expected": clj(res)}


@register("next_greater_circular")
def gen_next_greater_circular():
    n = random.randint(5, 10)
    nums = rand_list(n, -10, 10)
    res = [-1] * n
    for i in range(n):
        for j in range(1, n + 1):
            if nums[(i + j) % n] > nums[i]:
                res[i] = nums[(i + j) % n]
                break
    return {"args": clj([nums]), "expected": clj(res)}


@register("asteroid_collision")
def gen_asteroid_collision():
    n = random.randint(5, 10)
    ast = []
    for _ in range(n):
        size = random.randint(1, 8)
        if random.random() < 0.5:
            size = -size
        ast.append(size)
    stack = []
    for a in ast:
        alive = True
        while alive and a < 0 and stack and stack[-1] > 0:
            if stack[-1] < -a:
                stack.pop()
                continue
            if stack[-1] == -a:
                stack.pop()
            alive = False
        if alive:
            stack.append(a)
    return {"args": clj([ast]), "expected": clj(stack)}


@register("gas_station")
def gen_gas_station():
    n = random.randint(4, 8)
    gas = [random.randint(1, 6) for _ in range(n)]
    cost = [random.randint(1, 6) for _ in range(n)]
    total = sum(gas) - sum(cost)
    if total < 0:
        expected = -1
    else:
        tank = 0
        start = 0
        for i in range(n):
            tank += gas[i] - cost[i]
            if tank < 0:
                start = i + 1
                tank = 0
        expected = start
    return {"args": clj([gas, cost]), "expected": clj(expected)}


@register("jump_game")
def gen_jump_game():
    n = random.randint(5, 10)
    nums = [random.randint(0, 5) for _ in range(n)]
    reach = 0
    ok = True
    for i, v in enumerate(nums):
        if i > reach:
            ok = False
            break
        reach = max(reach, i + v)
    return {"args": clj([nums]), "expected": clj(ok)}


@register("jump_game_ii")
def gen_jump_game_ii():
    n = random.randint(5, 10)
    nums = [random.randint(1, 5) for _ in range(n - 1)] + [0]
    jumps = 0
    cur_end = 0
    far = 0
    for i in range(n - 1):
        far = max(far, i + nums[i])
        if i == cur_end:
            jumps += 1
            cur_end = far
    return {"args": clj([nums]), "expected": clj(jumps)}


@register("partition_labels")
def gen_partition_labels():
    s = rand_string(random.randint(6, 10), alphabet="abcde")
    last = {c: i for i, c in enumerate(s)}
    res = []
    start = end = 0
    for i, c in enumerate(s):
        end = max(end, last[c])
        if i == end:
            res.append(end - start + 1)
            start = i + 1
    return {"args": clj([s]), "expected": clj(res)}


@register("task_scheduler")
def gen_task_scheduler():
    tasks = [random.choice(list("ABCDEF")) for _ in range(random.randint(6, 12))]
    n = random.randint(1, 4)
    cnt = collections.Counter(tasks)
    maxf = max(cnt.values())
    num_max = sum(1 for v in cnt.values() if v == maxf)
    res = max(len(tasks), (maxf - 1) * (n + 1) + num_max)
    return {"args": clj([tasks, n]), "expected": clj(res)}


@register("longest_substring_no_repeat")
def gen_longest_substring_no_repeat():
    s = rand_string(random.randint(6, 12), alphabet="abcdabcde")
    seen = {}
    left = 0
    best = 0
    for i, ch in enumerate(s):
        if ch in seen and seen[ch] >= left:
            left = seen[ch] + 1
        seen[ch] = i
        best = max(best, i - left + 1)
    return {"args": clj([s]), "expected": clj(best)}


@register("longest_substring_k_distinct")
def gen_longest_substring_k_distinct():
    s = rand_string(random.randint(6, 12), alphabet="abcde")
    k = random.randint(1, 3)
    cnt = collections.Counter()
    left = 0
    best = 0
    for right, ch in enumerate(s):
        cnt[ch] += 1
        while len(cnt) > k:
            cnt[s[left]] -= 1
            if cnt[s[left]] == 0:
                del cnt[s[left]]
            left += 1
        best = max(best, right - left + 1)
    return {"args": clj([s, k]), "expected": clj(best)}


@register("min_window_substring")
def gen_min_window_substring():
    s = rand_string(random.randint(8, 14), alphabet="aabbbcddde")
    t = "".join(random.choice("abcde") for _ in range(random.randint(2, 4)))
    need = collections.Counter(t)
    missing = len(t)
    left = 0
    best = (math.inf, 0, 0)
    for right, ch in enumerate(s):
        if need[ch] > 0:
            missing -= 1
        need[ch] -= 1
        while missing == 0:
            if right - left + 1 < best[0]:
                best = (right - left + 1, left, right + 1)
            need[s[left]] += 1
            if need[s[left]] > 0:
                missing += 1
            left += 1
    out = "" if best[0] == math.inf else s[best[1]:best[2]]
    return {"args": clj([s, t]), "expected": clj(out)}


@register("longest_repeating_char_replace")
def gen_longest_repeating_char_replace():
    s = rand_string(random.randint(6, 12), alphabet="AABBCD")
    k = random.randint(1, 3)
    cnt = collections.Counter()
    left = 0
    best = 0
    maxf = 0
    for right, ch in enumerate(s):
        cnt[ch] += 1
        maxf = max(maxf, cnt[ch])
        while (right - left + 1) - maxf > k:
            cnt[s[left]] -= 1
            left += 1
        best = max(best, right - left + 1)
    return {"args": clj([s, k]), "expected": clj(best)}


@register("permutation_in_string")
def gen_permutation_in_string():
    s1 = rand_string(random.randint(2, 4), alphabet="abc")
    s2 = rand_string(random.randint(6, 10), alphabet="abc")
    need = collections.Counter(s1)
    window = collections.Counter()
    k = len(s1)
    ok = False
    for i, ch in enumerate(s2):
        window[ch] += 1
        if i >= k:
            window[s2[i - k]] -= 1
            if window[s2[i - k]] == 0:
                del window[s2[i - k]]
        if window == need:
            ok = True
            break
    return {"args": clj([s1, s2]), "expected": clj(ok)}


@register("find_anagrams")
def gen_find_anagrams():
    s = rand_string(random.randint(6, 10), alphabet="abc")
    p = rand_string(random.randint(2, 4), alphabet="abc")
    need = collections.Counter(p)
    window = collections.Counter()
    res = []
    k = len(p)
    for i, ch in enumerate(s):
        window[ch] += 1
        if i >= k:
            window[s[i - k]] -= 1
            if window[s[i - k]] == 0:
                del window[s[i - k]]
        if i >= k - 1 and window == need:
            res.append(i - k + 1)
    return {"args": clj([s, p]), "expected": clj(res)}


@register("valid_parentheses")
def gen_valid_parentheses():
    s = "".join(random.choice("()[]{}") for _ in range(random.randint(6, 10)))
    stack = []
    mapping = {")": "(", "]": "[", "}": "{"}
    ok = True
    for ch in s:
        if ch in mapping:
            if not stack or stack.pop() != mapping[ch]:
                ok = False
                break
        else:
            stack.append(ch)
    if stack:
        ok = False
    return {"args": clj([s]), "expected": clj(ok)}


@register("longest_valid_parentheses")
def gen_longest_valid_parentheses():
    s = "".join(random.choice("()") for _ in range(random.randint(8, 14)))
    stack = [-1]
    best = 0
    for i, ch in enumerate(s):
        if ch == "(":
            stack.append(i)
        else:
            stack.pop()
            if not stack:
                stack.append(i)
            else:
                best = max(best, i - stack[-1])
    return {"args": clj([s]), "expected": clj(best)}

@register("decode_ways")
def gen_decode_ways():
    s = "".join(random.choice("123456789") for _ in range(random.randint(3, 8)))
    dp0, dp1 = 1, 0
    for i, ch in enumerate(s):
        dp2 = 0
        if ch != "0":
            dp2 += dp0
        if i > 0 and s[i - 1] != "0" and 10 <= int(s[i - 1:i + 1]) <= 26:
            dp2 += dp1
        dp1, dp0 = dp0, dp2
    return {"args": clj([s]), "expected": clj(dp0)}


@register("word_break")
def gen_word_break():
    words = ["leet", "code", "apple", "pen", "cats", "dog"]
    s = random.choice(["leetcode", "applepenapple", "catsdog"])
    dict_words = random.sample(words, random.randint(2, 5))
    wordset = set(dict_words)
    n = len(s)
    dp = [False] * (n + 1)
    dp[0] = True
    for i in range(1, n + 1):
        for j in range(i):
            if dp[j] and s[j:i] in wordset:
                dp[i] = True
                break
    return {"args": clj([s, dict_words]), "expected": clj(dp[n])}


@register("word_break_ii")
def gen_word_break_ii():
    words = ["cat", "cats", "and", "sand", "dog"]
    s = random.choice(["catsanddog", "catsanddog"])
    wordset = set(words)
    memo = {}
    def dfs(i):
        if i == len(s):
            return [""]
        if i in memo:
            return memo[i]
        res = []
        for w in wordset:
            if s.startswith(w, i):
                for tail in dfs(i + len(w)):
                    res.append((w + (" " + tail if tail else "")).strip())
        memo[i] = res
        return res
    out = sorted(dfs(0))
    return {"args": clj([s, list(words)]), "expected": clj(out)}


@register("edit_distance")
def gen_edit_distance():
    a = rand_string(random.randint(4, 7), alphabet="abc")
    b = rand_string(random.randint(4, 7), alphabet="abc")
    n, m = len(a), len(b)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        dp[i][0] = i
    for j in range(m + 1):
        dp[0][j] = j
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1])
    return {"args": clj([a, b]), "expected": clj(dp[n][m])}


@register("lcs")
def gen_lcs():
    a = rand_string(random.randint(4, 7), alphabet="abcd")
    b = rand_string(random.randint(4, 7), alphabet="abcd")
    n, m = len(a), len(b)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n):
        for j in range(m):
            if a[i] == b[j]:
                dp[i + 1][j + 1] = dp[i][j] + 1
            else:
                dp[i + 1][j + 1] = max(dp[i][j + 1], dp[i + 1][j])
    return {"args": clj([a, b]), "expected": clj(dp[n][m])}


@register("lps")
def gen_lps():
    s = rand_string(random.randint(6, 10), alphabet="abcde")
    n = len(s)
    dp = [[0] * n for _ in range(n)]
    for i in range(n - 1, -1, -1):
        dp[i][i] = 1
        for j in range(i + 1, n):
            if s[i] == s[j]:
                dp[i][j] = dp[i + 1][j - 1] + 2
            else:
                dp[i][j] = max(dp[i + 1][j], dp[i][j - 1])
    return {"args": clj([s]), "expected": clj(dp[0][n - 1])}


@register("palindrome_partitioning")
def gen_pal_partitioning():
    s = random.choice(["aab", "abba", "aaba"])
    n = len(s)
    pal = [[False] * n for _ in range(n)]
    for i in range(n - 1, -1, -1):
        for j in range(i, n):
            if s[i] == s[j] and (j - i < 2 or pal[i + 1][j - 1]):
                pal[i][j] = True
    res = []
    def backtrack(i, path):
        if i == n:
            res.append(path[:])
            return
        for j in range(i, n):
            if pal[i][j]:
                backtrack(j + 1, path + [s[i:j + 1]])
    backtrack(0, [])
    res = sorted(res)
    return {"args": clj([s]), "expected": clj(res)}


@register("palindrome_partitioning_ii")
def gen_pal_partitioning_ii():
    s = rand_string(random.randint(6, 9), alphabet="abac")
    n = len(s)
    pal = [[False] * n for _ in range(n)]
    for i in range(n - 1, -1, -1):
        for j in range(i, n):
            if s[i] == s[j] and (j - i < 2 or pal[i + 1][j - 1]):
                pal[i][j] = True
    dp = [0] * n
    for i in range(n):
        if pal[0][i]:
            dp[i] = 0
        else:
            dp[i] = min(dp[j - 1] + 1 for j in range(1, i + 1) if pal[j][i])
    return {"args": clj([s]), "expected": clj(dp[-1])}


@register("regex_match")
def gen_regex_match():
    s = rand_string(random.randint(4, 7), alphabet="ab")
    p = random.choice(["a*b*", "ab*", ".*", "a.*b", "ab"])
    def is_match(s, p):
        return re.fullmatch(p, s) is not None
    return {"args": clj([s, p]), "expected": clj(is_match(s, p))}


@register("wildcard_match")
def gen_wildcard_match():
    s = rand_string(random.randint(4, 7), alphabet="ab")
    p = random.choice(["a*b", "*a?", "??", "a*"])
    def match(s, p):
        n, m = len(s), len(p)
        dp = [[False] * (m + 1) for _ in range(n + 1)]
        dp[0][0] = True
        for j in range(1, m + 1):
            if p[j - 1] == "*":
                dp[0][j] = dp[0][j - 1]
        for i in range(1, n + 1):
            for j in range(1, m + 1):
                if p[j - 1] == "*":
                    dp[i][j] = dp[i][j - 1] or dp[i - 1][j]
                elif p[j - 1] == "?" or p[j - 1] == s[i - 1]:
                    dp[i][j] = dp[i - 1][j - 1]
        return dp[n][m]
    return {"args": clj([s, p]), "expected": clj(match(s, p))}


@register("coin_change")
def gen_coin_change():
    coins = sorted(set(random.randint(1, 9) for _ in range(4)))
    amount = random.randint(6, 20)
    dp = [math.inf] * (amount + 1)
    dp[0] = 0
    for a in range(1, amount + 1):
        for c in coins:
            if a >= c and dp[a - c] != math.inf:
                dp[a] = min(dp[a], dp[a - c] + 1)
    res = -1 if dp[amount] == math.inf else dp[amount]
    return {"args": clj([coins, amount]), "expected": clj(res)}


@register("coin_change_2")
def gen_coin_change_2():
    coins = sorted(set(random.randint(1, 6) for _ in range(4)))
    amount = random.randint(6, 15)
    dp = [0] * (amount + 1)
    dp[0] = 1
    for c in coins:
        for a in range(c, amount + 1):
            dp[a] += dp[a - c]
    return {"args": clj([amount, coins]), "expected": clj(dp[amount])}


@register("target_sum")
def gen_target_sum():
    nums = [random.randint(0, 5) for _ in range(6)]
    target = random.randint(-5, 5)
    dp = collections.Counter()
    dp[0] = 1
    for x in nums:
        ndp = collections.Counter()
        for s, c in dp.items():
            ndp[s + x] += c
            ndp[s - x] += c
        dp = ndp
    return {"args": clj([nums, target]), "expected": clj(dp[target])}


@register("partition_equal_subset")
def gen_partition_equal_subset():
    nums = [random.randint(1, 9) for _ in range(8)]
    total = sum(nums)
    if total % 2 == 1:
        ok = False
    else:
        target = total // 2
        dp = {0}
        for x in nums:
            dp |= {s + x for s in list(dp) if s + x <= target}
        ok = target in dp
    return {"args": clj([nums]), "expected": clj(ok)}


@register("house_robber")
def gen_house_robber():
    nums = [random.randint(1, 10) for _ in range(8)]
    prev = cur = 0
    for x in nums:
        prev, cur = cur, max(cur, prev + x)
    return {"args": clj([nums]), "expected": clj(cur)}


@register("house_robber_ii")
def gen_house_robber_ii():
    nums = [random.randint(1, 10) for _ in range(8)]
    def rob(arr):
        prev = cur = 0
        for x in arr:
            prev, cur = cur, max(cur, prev + x)
        return cur
    res = max(nums[0], rob(nums[1:]), rob(nums[:-1]))
    return {"args": clj([nums]), "expected": clj(res)}


@register("delete_and_earn")
def gen_delete_and_earn():
    nums = [random.randint(1, 6) for _ in range(10)]
    cnt = collections.Counter(nums)
    maxv = max(cnt)
    take = skip = 0
    prev = None
    for v in range(1, maxv + 1):
        gain = v * cnt.get(v, 0)
        if prev == v - 1:
            take, skip = skip + gain, max(skip, take)
        else:
            take, skip = max(skip, take) + gain, max(skip, take)
        prev = v
    return {"args": clj([nums]), "expected": clj(max(take, skip))}


@register("stock_cooldown")
def gen_stock_cooldown():
    prices = [random.randint(1, 10) for _ in range(8)]
    hold = -prices[0]
    sold = 0
    rest = 0
    for p in prices[1:]:
        prev_sold = sold
        sold = hold + p
        hold = max(hold, rest - p)
        rest = max(rest, prev_sold)
    return {"args": clj([prices]), "expected": clj(max(sold, rest))}


@register("stock_fee")
def gen_stock_fee():
    prices = [random.randint(1, 10) for _ in range(8)]
    fee = random.randint(1, 3)
    hold = -prices[0]
    cash = 0
    for p in prices[1:]:
        cash = max(cash, hold + p - fee)
        hold = max(hold, cash - p)
    return {"args": clj([prices, fee]), "expected": clj(cash)}


@register("stock_iii")
def gen_stock_iii():
    prices = [random.randint(1, 10) for _ in range(8)]
    buy1 = -math.inf
    buy2 = -math.inf
    sell1 = 0
    sell2 = 0
    for p in prices:
        buy1 = max(buy1, -p)
        sell1 = max(sell1, buy1 + p)
        buy2 = max(buy2, sell1 - p)
        sell2 = max(sell2, buy2 + p)
    return {"args": clj([prices]), "expected": clj(sell2)}


@register("lis")
def gen_lis():
    nums = rand_list(10, -10, 10)
    tails = []
    for x in nums:
        i = bisect.bisect_left(tails, x)
        if i == len(tails):
            tails.append(x)
        else:
            tails[i] = x
    return {"args": clj([nums]), "expected": clj(len(tails))}


@register("num_lis")
def gen_num_lis():
    nums = rand_list(10, -5, 5)
    n = len(nums)
    dp = [1] * n
    cnt = [1] * n
    for i in range(n):
        for j in range(i):
            if nums[j] < nums[i]:
                if dp[j] + 1 > dp[i]:
                    dp[i] = dp[j] + 1
                    cnt[i] = cnt[j]
                elif dp[j] + 1 == dp[i]:
                    cnt[i] += cnt[j]
    longest = max(dp)
    total = sum(cnt[i] for i in range(n) if dp[i] == longest)
    return {"args": clj([nums]), "expected": clj(total)}


@register("russian_doll")
def gen_russian_doll():
    envs = []
    for _ in range(8):
        w = random.randint(1, 10)
        h = random.randint(1, 10)
        envs.append([w, h])
    envs.sort(key=lambda x: (x[0], -x[1]))
    heights = [h for _, h in envs]
    tails = []
    for x in heights:
        i = bisect.bisect_left(tails, x)
        if i == len(tails):
            tails.append(x)
        else:
            tails[i] = x
    return {"args": clj([envs]), "expected": clj(len(tails))}


@register("maximal_square")
def gen_maximal_square():
    rows = random.randint(3, 6)
    cols = random.randint(3, 6)
    grid = [[random.choice(["0", "1"]) for _ in range(cols)] for _ in range(rows)]
    dp = [[0] * (cols + 1) for _ in range(rows + 1)]
    best = 0
    for i in range(1, rows + 1):
        for j in range(1, cols + 1):
            if grid[i - 1][j - 1] == "1":
                dp[i][j] = 1 + min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1])
                best = max(best, dp[i][j])
    return {"args": clj([grid]), "expected": clj(best * best)}


@register("unique_paths_ii")
def gen_unique_paths_ii():
    m = random.randint(3, 6)
    n = random.randint(3, 6)
    grid = [[0 for _ in range(n)] for _ in range(m)]
    for _ in range(random.randint(1, 3)):
        grid[random.randint(0, m - 1)][random.randint(0, n - 1)] = 1
    dp = [[0] * n for _ in range(m)]
    dp[0][0] = 0 if grid[0][0] == 1 else 1
    for i in range(m):
        for j in range(n):
            if grid[i][j] == 1:
                dp[i][j] = 0
            else:
                if i > 0:
                    dp[i][j] += dp[i - 1][j]
                if j > 0:
                    dp[i][j] += dp[i][j - 1]
    return {"args": clj([grid]), "expected": clj(dp[m - 1][n - 1])}


@register("min_path_sum")
def gen_min_path_sum():
    m = random.randint(3, 6)
    n = random.randint(3, 6)
    grid = [[random.randint(1, 9) for _ in range(n)] for _ in range(m)]
    dp = [[0] * n for _ in range(m)]
    dp[0][0] = grid[0][0]
    for i in range(m):
        for j in range(n):
            if i == 0 and j == 0:
                continue
            dp[i][j] = grid[i][j] + min(
                dp[i - 1][j] if i > 0 else math.inf,
                dp[i][j - 1] if j > 0 else math.inf
            )
    return {"args": clj([grid]), "expected": clj(dp[m - 1][n - 1])}


@register("triangle_min_path")
def gen_triangle_min_path():
    rows = random.randint(4, 6)
    triangle = []
    for i in range(rows):
        triangle.append([random.randint(1, 9) for _ in range(i + 1)])
    dp = triangle[-1][:]
    for i in range(rows - 2, -1, -1):
        for j in range(i + 1):
            dp[j] = triangle[i][j] + min(dp[j], dp[j + 1])
    return {"args": clj([triangle]), "expected": clj(dp[0])}


@register("num_islands")
def gen_num_islands():
    m = random.randint(3, 6)
    n = random.randint(3, 6)
    grid = [[random.choice(["0", "1"]) for _ in range(n)] for _ in range(m)]
    seen = [[False] * n for _ in range(m)]
    def dfs(r, c):
        stack = [(r, c)]
        seen[r][c] = True
        while stack:
            x, y = stack.pop()
            for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < m and 0 <= ny < n and not seen[nx][ny] and grid[nx][ny] == "1":
                    seen[nx][ny] = True
                    stack.append((nx, ny))
    count = 0
    for i in range(m):
        for j in range(n):
            if grid[i][j] == "1" and not seen[i][j]:
                count += 1
                dfs(i, j)
    return {"args": clj([grid]), "expected": clj(count)}


@register("max_area_island")
def gen_max_area_island():
    m = random.randint(3, 6)
    n = random.randint(3, 6)
    grid = [[random.randint(0, 1) for _ in range(n)] for _ in range(m)]
    seen = [[False] * n for _ in range(m)]
    def dfs(r, c):
        stack = [(r, c)]
        seen[r][c] = True
        area = 0
        while stack:
            x, y = stack.pop()
            area += 1
            for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < m and 0 <= ny < n and not seen[nx][ny] and grid[nx][ny] == 1:
                    seen[nx][ny] = True
                    stack.append((nx, ny))
        return area
    best = 0
    for i in range(m):
        for j in range(n):
            if grid[i][j] == 1 and not seen[i][j]:
                best = max(best, dfs(i, j))
    return {"args": clj([grid]), "expected": clj(best)}


@register("pacific_atlantic")
def gen_pacific_atlantic():
    m = random.randint(3, 5)
    n = random.randint(3, 5)
    heights = [[random.randint(0, 9) for _ in range(n)] for _ in range(m)]
    def bfs(starts):
        reachable = [[False]*n for _ in range(m)]
        q = collections.deque(starts)
        for r, c in starts:
            reachable[r][c] = True
        while q:
            r, c = q.popleft()
            for dr, dc in ((1,0),(-1,0),(0,1),(0,-1)):
                nr, nc = r + dr, c + dc
                if 0 <= nr < m and 0 <= nc < n and not reachable[nr][nc] and heights[nr][nc] >= heights[r][c]:
                    reachable[nr][nc] = True
                    q.append((nr, nc))
        return reachable
    pacific_starts = [(0, c) for c in range(n)] + [(r, 0) for r in range(m)]
    atlantic_starts = [(m - 1, c) for c in range(n)] + [(r, n - 1) for r in range(m)]
    pac = bfs(pacific_starts)
    atl = bfs(atlantic_starts)
    res = []
    for i in range(m):
        for j in range(n):
            if pac[i][j] and atl[i][j]:
                res.append([i, j])
    res.sort()
    return {"args": clj([heights]), "expected": clj(res)}


@register("surrounded_regions")
def gen_surrounded_regions():
    m = random.randint(3, 5)
    n = random.randint(3, 5)
    board = [[random.choice(["X", "O"]) for _ in range(n)] for _ in range(m)]
    seen = [[False]*n for _ in range(m)]
    def dfs(r, c):
        stack = [(r, c)]
        seen[r][c] = True
        while stack:
            x, y = stack.pop()
            for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < m and 0 <= ny < n and not seen[nx][ny] and board[nx][ny] == "O":
                    seen[nx][ny] = True
                    stack.append((nx, ny))
    for i in range(m):
        for j in range(n):
            if i in (0, m - 1) or j in (0, n - 1):
                if board[i][j] == "O" and not seen[i][j]:
                    dfs(i, j)
    out = [row[:] for row in board]
    for i in range(m):
        for j in range(n):
            if out[i][j] == "O" and not seen[i][j]:
                out[i][j] = "X"
    return {"args": clj([board]), "expected": clj(out)}


@register("course_schedule")
def gen_course_schedule():
    n = random.randint(4, 7)
    edges = []
    for _ in range(random.randint(3, 7)):
        a = random.randint(0, n - 1)
        b = random.randint(0, n - 1)
        if a != b:
            edges.append([a, b])
    graph = [[] for _ in range(n)]
    indeg = [0] * n
    for a, b in edges:
        graph[b].append(a)
        indeg[a] += 1
    q = collections.deque([i for i in range(n) if indeg[i] == 0])
    seen = 0
    while q:
        u = q.popleft()
        seen += 1
        for v in graph[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)
    return {"args": clj([n, edges]), "expected": clj(seen == n)}


@register("course_schedule_ii")
def gen_course_schedule_ii():
    n = random.randint(4, 7)
    edges = []
    for _ in range(random.randint(3, 7)):
        a = random.randint(0, n - 1)
        b = random.randint(0, n - 1)
        if a != b:
            edges.append([a, b])
    graph = [[] for _ in range(n)]
    indeg = [0] * n
    for a, b in edges:
        graph[b].append(a)
        indeg[a] += 1
    q = collections.deque([i for i in range(n) if indeg[i] == 0])
    order = []
    while q:
        u = q.popleft()
        order.append(u)
        for v in graph[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)
    if len(order) != n:
        order = []
    return {"args": clj([n, edges]), "expected": clj(order)}


@register("network_delay")
def gen_network_delay():
    n = random.randint(4, 6)
    edges = []
    for _ in range(random.randint(5, 10)):
        u = random.randint(1, n)
        v = random.randint(1, n)
        if u != v:
            w = random.randint(1, 9)
            edges.append([u, v, w])
    k = random.randint(1, n)
    graph = collections.defaultdict(list)
    for u, v, w in edges:
        graph[u].append((v, w))
    dist = {i: math.inf for i in range(1, n + 1)}
    dist[k] = 0
    heap = [(0, k)]
    while heap:
        d, u = heapq.heappop(heap)
        if d != dist[u]:
            continue
        for v, w in graph[u]:
            nd = d + w
            if nd < dist[v]:
                dist[v] = nd
                heapq.heappush(heap, (nd, v))
    ans = max(dist.values())
    return {"args": clj([edges, n, k]), "expected": clj(-1 if ans == math.inf else ans)}


@register("cheapest_flights_k")
def gen_cheapest_flights_k():
    n = random.randint(4, 6)
    flights = []
    for _ in range(random.randint(6, 10)):
        u = random.randint(0, n - 1)
        v = random.randint(0, n - 1)
        if u != v:
            flights.append([u, v, random.randint(1, 9)])
    src = random.randint(0, n - 1)
    dst = random.randint(0, n - 1)
    k = random.randint(0, 2)
    dist = [math.inf] * n
    dist[src] = 0
    for _ in range(k + 1):
        nd = dist[:]
        for u, v, w in flights:
            if dist[u] + w < nd[v]:
                nd[v] = dist[u] + w
        dist = nd
    return {"args": clj([n, flights, src, dst, k]), "expected": clj(-1 if dist[dst] == math.inf else dist[dst])}


@register("rotting_oranges")
def gen_rotting_oranges():
    m = random.randint(3, 5)
    n = random.randint(3, 5)
    grid = [[random.randint(0, 2) for _ in range(n)] for _ in range(m)]
    q = collections.deque()
    fresh = 0
    for i in range(m):
        for j in range(n):
            if grid[i][j] == 2:
                q.append((i, j))
            elif grid[i][j] == 1:
                fresh += 1
    minutes = 0
    while q and fresh > 0:
        for _ in range(len(q)):
            x, y = q.popleft()
            for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < m and 0 <= ny < n and grid[nx][ny] == 1:
                    grid[nx][ny] = 2
                    fresh -= 1
                    q.append((nx, ny))
        minutes += 1
    return {"args": clj([grid]), "expected": clj(-1 if fresh > 0 else minutes)}


@register("shortest_path_binary_matrix")
def gen_shortest_path_binary_matrix():
    n = random.randint(3, 5)
    grid = [[random.randint(0, 1) for _ in range(n)] for _ in range(n)]
    if grid[0][0] == 1 or grid[n - 1][n - 1] == 1:
        return {"args": clj([grid]), "expected": clj(-1)}
    q = collections.deque([(0, 0, 1)])
    seen = {(0, 0)}
    res = -1
    while q:
        x, y, d = q.popleft()
        if x == n - 1 and y == n - 1:
            res = d
            break
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < n and 0 <= ny < n and grid[nx][ny] == 0 and (nx, ny) not in seen:
                    seen.add((nx, ny))
                    q.append((nx, ny, d + 1))
    return {"args": clj([grid]), "expected": clj(res)}


@register("min_cost_connect_points")
def gen_min_cost_connect_points():
    n = random.randint(4, 7)
    points = [[random.randint(0, 10), random.randint(0, 10)] for _ in range(n)]
    dist = [math.inf] * n
    dist[0] = 0
    used = [False] * n
    res = 0
    for _ in range(n):
        u = min((d, i) for i, d in enumerate(dist) if not used[i])[1]
        used[u] = True
        res += dist[u]
        for v in range(n):
            if not used[v]:
                w = abs(points[u][0] - points[v][0]) + abs(points[u][1] - points[v][1])
                if w < dist[v]:
                    dist[v] = w
    return {"args": clj([points]), "expected": clj(res)}

@register("redundant_connection")
def gen_redundant_connection():
    n = random.randint(4, 7)
    edges = []
    parent = list(range(n + 1))
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    def union(a, b):
        ra, rb = find(a), find(b)
        if ra == rb:
            return False
        parent[rb] = ra
        return True
    for i in range(2, n + 1):
        edges.append([i, random.randint(1, i - 1)])
    extra = random.choice(edges)
    edges.append(extra)
    red = None
    parent = list(range(n + 1))
    for a, b in edges:
        if not union(a, b):
            red = [a, b]
    return {"args": clj([edges]), "expected": clj(red)}


@register("evaluate_division")
def gen_evaluate_division():
    equations = [["a", "b"], ["b", "c"], ["c", "d"]]
    values = [2.0, 3.0, 4.0]
    queries = [["a", "c"], ["b", "a"], ["a", "e"]]
    graph = collections.defaultdict(list)
    for (u, v), w in zip(equations, values):
        graph[u].append((v, w))
        graph[v].append((u, 1.0 / w))
    def query(u, v):
        if u not in graph or v not in graph:
            return -1.0
        q = collections.deque([(u, 1.0)])
        seen = {u}
        while q:
            node, val = q.popleft()
            if node == v:
                return val
            for nxt, w in graph[node]:
                if nxt not in seen:
                    seen.add(nxt)
                    q.append((nxt, val * w))
        return -1.0
    res = [query(u, v) for u, v in queries]
    return {"args": clj([equations, values, queries]), "expected": clj(res)}


@register("largest_histogram")
def gen_largest_histogram():
    heights = [random.randint(1, 8) for _ in range(random.randint(6, 10))]
    stack = []
    best = 0
    for i, h in enumerate(heights + [0]):
        while stack and heights[stack[-1]] > h:
            height = heights[stack.pop()]
            start = stack[-1] + 1 if stack else 0
            best = max(best, height * (i - start))
        stack.append(i)
    return {"args": clj([heights]), "expected": clj(best)}


@register("maximal_rectangle")
def gen_maximal_rectangle():
    rows = random.randint(3, 5)
    cols = random.randint(3, 5)
    matrix = [[random.choice(["0", "1"]) for _ in range(cols)] for _ in range(rows)]
    heights = [0] * cols
    best = 0
    for r in range(rows):
        for c in range(cols):
            if matrix[r][c] == "1":
                heights[c] += 1
            else:
                heights[c] = 0
        stack = []
        for i, h in enumerate(heights + [0]):
            while stack and heights[stack[-1]] > h:
                height = heights[stack.pop()]
                start = stack[-1] + 1 if stack else 0
                best = max(best, height * (i - start))
            stack.append(i)
    return {"args": clj([matrix]), "expected": clj(best)}


@register("kth_smallest_matrix")
def gen_kth_smallest_matrix():
    n = random.randint(3, 5)
    base = sorted(rand_list(n * n, -5, 10))
    matrix = [base[i * n:(i + 1) * n] for i in range(n)]
    for i in range(n):
        matrix[i].sort()
    for j in range(n):
        col = sorted(matrix[i][j] for i in range(n))
        for i in range(n):
            matrix[i][j] = col[i]
    k = random.randint(1, n * n)
    expected = sorted([x for row in matrix for x in row])[k - 1]
    return {"args": clj([matrix, k]), "expected": clj(expected)}


@register("search_2d_matrix_ii")
def gen_search_2d_matrix_ii():
    m = random.randint(3, 5)
    n = random.randint(3, 5)
    base = sorted(rand_list(m * n, -10, 20))
    matrix = [base[i * n:(i + 1) * n] for i in range(m)]
    target = random.choice(base + [999])
    found = any(target in row for row in matrix)
    return {"args": clj([matrix, target]), "expected": clj(found)}


@register("word_search")
def gen_word_search():
    m = random.randint(3, 5)
    n = random.randint(3, 5)
    board = [[random.choice(list("abcd")) for _ in range(n)] for _ in range(m)]
    word = "".join(random.choice(list("abcd")) for _ in range(random.randint(3, 5)))
    def exist():
        def dfs(r, c, i):
            if i == len(word):
                return True
            if not (0 <= r < m and 0 <= c < n) or board[r][c] != word[i]:
                return False
            tmp = board[r][c]
            board[r][c] = "#"
            ok = dfs(r + 1, c, i + 1) or dfs(r - 1, c, i + 1) or dfs(r, c + 1, i + 1) or dfs(r, c - 1, i + 1)
            board[r][c] = tmp
            return ok
        for i in range(m):
            for j in range(n):
                if dfs(i, j, 0):
                    return True
        return False
    ok = exist()
    return {"args": clj([board, word]), "expected": clj(ok)}


@register("dungeon_game")
def gen_dungeon_game():
    m = random.randint(3, 5)
    n = random.randint(3, 5)
    dungeon = [[random.randint(-5, 5) for _ in range(n)] for _ in range(m)]
    dp = [[0] * n for _ in range(m)]
    for i in range(m - 1, -1, -1):
        for j in range(n - 1, -1, -1):
            if i == m - 1 and j == n - 1:
                dp[i][j] = max(1, 1 - dungeon[i][j])
            else:
                need = min(
                    dp[i + 1][j] if i + 1 < m else math.inf,
                    dp[i][j + 1] if j + 1 < n else math.inf
                )
                dp[i][j] = max(1, need - dungeon[i][j])
    return {"args": clj([dungeon]), "expected": clj(dp[0][0])}


@register("min_window_subsequence")
def gen_min_window_subsequence():
    s = rand_string(random.randint(8, 12), alphabet="abcde")
    t = rand_string(random.randint(2, 4), alphabet="abcde")
    best = ""
    best_len = math.inf
    for i in range(len(s)):
        if s[i] != t[0]:
            continue
        si = i
        ti = 0
        while si < len(s) and ti < len(t):
            if s[si] == t[ti]:
                ti += 1
            si += 1
        if ti == len(t):
            end = si
            ti -= 1
            si -= 1
            while si >= i:
                if s[si] == t[ti]:
                    ti -= 1
                    if ti < 0:
                        break
                si -= 1
            start = si + 1
            if end - start < best_len:
                best_len = end - start
                best = s[start:end]
    return {"args": clj([s, t]), "expected": clj(best)}


@register("longest_palindromic_substring")
def gen_longest_palindromic_substring():
    s = rand_string(random.randint(6, 10), alphabet="abac")
    best = ""
    for i in range(len(s)):
        for j in range(i, len(s)):
            sub = s[i:j + 1]
            if sub == sub[::-1] and len(sub) > len(best):
                best = sub
    return {"args": clj([s]), "expected": clj(best)}


@register("zigzag_conversion")
def gen_zigzag_conversion():
    s = rand_string(random.randint(6, 10), alphabet="abcdef")
    num_rows = random.randint(2, 4)
    rows = [""] * num_rows
    idx = 0
    step = 1
    for ch in s:
        rows[idx] += ch
        if idx == 0:
            step = 1
        elif idx == num_rows - 1:
            step = -1
        idx += step
    return {"args": clj([s, num_rows]), "expected": clj("".join(rows))}


@register("generate_parentheses")
def gen_generate_parentheses():
    n = random.randint(2, 4)
    res = []
    def backtrack(s, open_c, close_c):
        if len(s) == 2 * n:
            res.append(s)
            return
        if open_c < n:
            backtrack(s + "(", open_c + 1, close_c)
        if close_c < open_c:
            backtrack(s + ")", open_c, close_c + 1)
    backtrack("", 0, 0)
    res.sort()
    return {"args": clj([n]), "expected": clj(res)}


@register("combination_sum")
def gen_combination_sum():
    candidates = sorted(set(random.randint(2, 9) for _ in range(4)))
    target = random.randint(7, 15)
    res = []
    def backtrack(start, total, path):
        if total == target:
            res.append(path[:])
            return
        if total > target:
            return
        for i in range(start, len(candidates)):
            backtrack(i, total + candidates[i], path + [candidates[i]])
    backtrack(0, 0, [])
    res = sorted(res)
    return {"args": clj([candidates, target]), "expected": clj(res)}


@register("combination_sum_ii")
def gen_combination_sum_ii():
    candidates = [random.randint(1, 8) for _ in range(6)]
    target = random.randint(6, 15)
    candidates.sort()
    res = []
    def backtrack(start, total, path):
        if total == target:
            res.append(path[:])
            return
        if total > target:
            return
        prev = None
        for i in range(start, len(candidates)):
            if prev is not None and candidates[i] == prev:
                continue
            prev = candidates[i]
            backtrack(i + 1, total + candidates[i], path + [candidates[i]])
    backtrack(0, 0, [])
    res = sorted(res)
    return {"args": clj([candidates, target]), "expected": clj(res)}


@register("subsets_ii")
def gen_subsets_ii():
    nums = [random.randint(1, 4) for _ in range(5)]
    nums.sort()
    res = []
    def backtrack(start, path):
        res.append(path[:])
        prev = None
        for i in range(start, len(nums)):
            if prev is not None and nums[i] == prev:
                continue
            prev = nums[i]
            backtrack(i + 1, path + [nums[i]])
    backtrack(0, [])
    res = sorted(res)
    return {"args": clj([nums]), "expected": clj(res)}


@register("permutations_ii")
def gen_permutations_ii():
    nums = [random.randint(1, 3) for _ in range(4)]
    res = set(itertools.permutations(nums))
    out = sorted([list(x) for x in res])
    return {"args": clj([nums]), "expected": clj(out)}


@register("validate_sudoku")
def gen_validate_sudoku():
    board = [["." for _ in range(9)] for _ in range(9)]
    for _ in range(15):
        r = random.randint(0, 8)
        c = random.randint(0, 8)
        board[r][c] = str(random.randint(1, 9))
    def is_valid(board):
        for i in range(9):
            row = [c for c in board[i] if c != "."]
            if len(set(row)) != len(row):
                return False
            col = [board[r][i] for r in range(9) if board[r][i] != "."]
            if len(set(col)) != len(col):
                return False
        for br in range(0, 9, 3):
            for bc in range(0, 9, 3):
                cell = []
                for r in range(br, br + 3):
                    for c in range(bc, bc + 3):
                        if board[r][c] != ".":
                            cell.append(board[r][c])
                if len(set(cell)) != len(cell):
                    return False
        return True
    return {"args": clj([board]), "expected": clj(is_valid(board))}


@register("split_array_largest_sum")
def gen_split_array_largest_sum():
    nums = [random.randint(1, 9) for _ in range(8)]
    m = random.randint(2, 4)
    def can(mid):
        count = 1
        total = 0
        for x in nums:
            if total + x > mid:
                count += 1
                total = x
            else:
                total += x
        return count <= m
    lo, hi = max(nums), sum(nums)
    while lo < hi:
        mid = (lo + hi) // 2
        if can(mid):
            hi = mid
        else:
            lo = mid + 1
    return {"args": clj([nums, m]), "expected": clj(lo)}


@register("min_cost_tickets")
def gen_min_cost_tickets():
    days = sorted(random.sample(range(1, 31), 8))
    costs = [random.randint(2, 5), random.randint(7, 10), random.randint(15, 20)]
    dayset = set(days)
    last = days[-1]
    dp = [0] * (last + 1)
    for d in range(1, last + 1):
        if d not in dayset:
            dp[d] = dp[d - 1]
        else:
            dp[d] = min(
                dp[max(0, d - 1)] + costs[0],
                dp[max(0, d - 7)] + costs[1],
                dp[max(0, d - 30)] + costs[2]
            )
    return {"args": clj([days, costs]), "expected": clj(dp[last])}


@register("longest_increasing_path")
def gen_longest_increasing_path():
    m = random.randint(3, 5)
    n = random.randint(3, 5)
    matrix = [[random.randint(0, 9) for _ in range(n)] for _ in range(m)]
    memo = [[0] * n for _ in range(m)]
    def dfs(r, c):
        if memo[r][c] != 0:
            return memo[r][c]
        best = 1
        for dr, dc in ((1,0),(-1,0),(0,1),(0,-1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < m and 0 <= nc < n and matrix[nr][nc] > matrix[r][c]:
                best = max(best, 1 + dfs(nr, nc))
        memo[r][c] = best
        return best
    ans = 0
    for i in range(m):
        for j in range(n):
            ans = max(ans, dfs(i, j))
    return {"args": clj([matrix]), "expected": clj(ans)}


@register("shortest_bridge")
def gen_shortest_bridge():
    n = random.randint(3, 5)
    grid = [[0 for _ in range(n)] for _ in range(n)]
    # create two single-cell islands
    a = (random.randint(0, n - 1), random.randint(0, n - 1))
    b = a
    while b == a:
        b = (random.randint(0, n - 1), random.randint(0, n - 1))
    grid[a[0]][a[1]] = 1
    grid[b[0]][b[1]] = 1
    q = collections.deque()
    seen = [[False]*n for _ in range(n)]
    def mark(r, c):
        stack = [(r, c)]
        seen[r][c] = True
        while stack:
            x, y = stack.pop()
            q.append((x, y, 0))
            for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < n and 0 <= ny < n and not seen[nx][ny] and grid[nx][ny] == 1:
                    seen[nx][ny] = True
                    stack.append((nx, ny))
    mark(a[0], a[1])
    res = 0
    while q:
        x, y, d = q.popleft()
        for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < n and 0 <= ny < n and not seen[nx][ny]:
                if grid[nx][ny] == 1:
                    res = d
                    q.clear()
                    break
                seen[nx][ny] = True
                q.append((nx, ny, d + 1))
    return {"args": clj([grid]), "expected": clj(res)}


@register("min_genetic_mutation")
def gen_min_genetic_mutation():
    genes = ["AACCGGTT", "AACCGGTA", "AACCGCTA", "AAACGGTA"]
    start = "AACCGGTT"
    end = "AAACGGTA"
    bank = genes
    bank_set = set(bank)
    if end not in bank_set:
        return {"args": clj([start, end, bank]), "expected": clj(-1)}
    q = collections.deque([(start, 0)])
    seen = {start}
    def neighbors(g):
        for i, ch in enumerate(g):
            for c in "ACGT":
                if c != ch:
                    ng = g[:i] + c + g[i+1:]
                    if ng in bank_set:
                        yield ng
    res = -1
    while q:
        g, d = q.popleft()
        if g == end:
            res = d
            break
        for ng in neighbors(g):
            if ng not in seen:
                seen.add(ng)
                q.append((ng, d + 1))
    return {"args": clj([start, end, bank]), "expected": clj(res)}


@register("diameter_binary_tree")
def gen_diameter_binary_tree():
    arr = [random.randint(1, 9) if random.random() < 0.7 else None for _ in range(15)]
    root = list_to_tree(arr)
    best = 0
    def depth(node):
        nonlocal best
        if not node:
            return 0
        l = depth(node.left)
        r = depth(node.right)
        best = max(best, l + r)
        return max(l, r) + 1
    depth(root)
    return {"args": clj([tree_to_list(root)]), "expected": clj(best)}
