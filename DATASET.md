# Colosseum Challenge Dataset

The dataset for this challenge is hosted on [HuggingFace][0]. I consists of
various `tar` files containing the data for variations on each of the 20 tasks.

## Downloading the dataset using wget and a download link

1. Go to the HuggingFace repo and select the files option:

![img-hf-files](./media/img_huggingface_files_section.png)

2. Select the task you want to get:

![img-hf-task](./media/img_huggingface_task_selection.png)

3. Get the download link:

![img-hf-download-link](./media/img_huggingface_download_link.png)

4. Use `curl` or `wget` to get the tar file:

```bash
wget YOUR_DOWNLOAD_LINK
```


[0]: <https://huggingface.co/datasets/colosseum/colosseum-challenge/tree/main> (huggingface-dataset)
