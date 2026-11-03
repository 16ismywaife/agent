class solution{
    public:
    int removechongfu(vector<int>& nums){
        if(nums.empty()) return 0;
        int zuo=1;
        for(int you=1;you<nums.size();you++){
            if(nums[you]!=nums[zuo-1]){
                nums[zuo]=nums[you];
                zuo++;
            }
        }
        return zuo;
    }
}


class solution{
    public:
    int removexiangtong(vector<int>& nums,int val){
        int zuo=0;
        for(int you=0;you<nums.size();you++){
            if(nums[you]!=val){
                nums[zuo]=nums[you];
                zuo++;
            }
        }
        return zuo;
    }
}

#0,1,1,2,2,3,4,4,5