import torch

print("PyTorch version:", torch.__version__)
print("CUDA in PyTorch:", torch.version.cuda)
print("CUDA available:", torch.cuda.is_available())
print("cuDNN available:", torch.backends.cudnn.is_available())
