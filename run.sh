dir=/Users/m216613
input_dir=$dir/Downloads/data
output_dir=$dir/Downloads/results
code_dir=$dir/PycharmProjects/Cell-Nuclei-Detection-and-Segmentation/
cd $code_dir
model_name='nucles_model_v3.meta'
image_format='.png'
no_warn_op='True'
/Users/m216613/Anaconda/tf1/bin/python /Users/m216613/PycharmProjects/Cell-Nuclei-Detection-and-Segmentation/main.py -i $input_dir -o $output_dir -m $model_name -f $image_format -w $no_warn_op