dir=/Users/m216613
input_dir=$dir/Downloads/data
output_dir=$dir/Downloads/results
coord_dir=$dir/Downloads/file
img_array_dir=$dir
is_img_np='False'
is_seg='True'
is_pickle='True'
is_load='True'
coord_name='cell_nuclei_seg_coord.pkl'
code_dir=$dir/PycharmProjects/Cell-Nuclei-Detection-and-Segmentation/
cd $code_dir
model_name='nucles_model_v3.meta'
image_format='.png'
no_warn_op='True'
/Users/m216613/Anaconda/tf1/bin/python /Users/m216613/PycharmProjects/Cell-Nuclei-Detection-and-Segmentation/main.py -a $img_array_dir -i $input_dir -o $output_dir -d $coord_dir -c $coord_name -m $model_name -f $image_format -s $is_seg -p $is_pickle -l $is_load -n $is_img_np -w $no_warn_op