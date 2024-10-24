#! bin/bash
# 参考：
# 1. Hugin Help(软件离线帮助文档)-->Tips and Tricks/scripting
# 2. https://medium.com/stereopi/stitching-360-panorama-with-raspberry-pi-cm3-stereopi-and-two-fisheye-cameras-step-by-step-guide-aeca3ff35871
# 3. https://hugin.sourceforge.io/tutorials/enfuse-360/en.shtml
#
# 利用pto文件批量化对dualFisheye图像进行全景拼接，ffmpeg合成视频，主要就是下面2个步骤

# nona -o out -m TIFF_m frontback.pto front.png back.png #得到out0000.tif,out0001.tif，分别对应front00538.png,back00538.png的映射矩阵,即从dualfish到equirectgular映射
# enblend -o out.png out0000.tif out0001.tif # 由out0000.tif和out0001.tif得到最终的融合图


# 初始化循环变量idx
idx=1

# 使用while循环遍历图像文件
while (( 2 * idx <= $(ls -1 pairImagesD | wc -l)-1 ))
do
    # 获取两张图片文件名
    file1=$(printf "~/allData/pairImagesD/%04d.png" $((2 * idx - 1))) # front鱼眼原始图
    file2=$(printf "~/allData/pairImagesD/%04d.png" $((2 * idx))) # back鱼眼原始图
    
    # 可以在这里执行你想要的操作，比如输出文件名
    echo "Image 1: $file1"
    echo "Image 2: $file2"
    
    nona -o out -m TIFF_m newTemplate.pto $file1 $file2 # 这里修改为自己的配置模板文件pto
    dstfile=$(printf "results2/%05d.png" $((idx)))
    echo "dstfile : $dstfile"
    enblend -o $dstfile out0000.tif out0001.tif 

    # 更新idx
    ((idx++))
done

# 设定图片文件夹路径
image_folder="results2"

# 设定输出视频文件名
output_video="20240607outputNew.mp4"

# 使用FFmpeg将图片合成为视频
# ffmpeg -f image2 -framerate 25 -pattern_type glob -i "$image_folder/*.png" -c:v copy  "$output_video"
ffmpeg -framerate 30 -i "$image_folder/*.png" -c:v libx264 -r 30 -pix_fmt yuv420p "$output_video"