class Solution:
    def removeElement(self, nums: List[int], val: int) -> int:
        for i in range(len(nums)+1):
            try:
                nums.remove(val)
            except:
                pass

        return len(nums)