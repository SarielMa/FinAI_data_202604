# export HF_HUB_ENABLE_HF_TRANSFER=1

# hf upload TheFinAI/freebsd-cvs-archive freebsd_output_ready_for_HF/ --repo-type dataset
# hf upload-large-folder TheFinAI/freebsd-cvs-archive freebsd_output_ready_for_HF --repo-type dataset

hf repo create TheFinAI/freebsd-cvs-archive-xet --type dataset

HF_HUB_ENABLE_XET=1 hf upload-large-folder \
  TheFinAI/freebsd-cvs-archive-xet \
  freebsd_output_ready_for_HF \
  --repo-type dataset