import torch
from diffusers import StableDiffusionPipeline

# Check GPU
device = "cuda" if torch.cuda.is_available() else "cpu"
print("Using:", device)

# Load Stable Diffusion model
pipe = StableDiffusionPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    torch_dtype=torch.float16 if device == "cuda" else torch.float32
)

pipe = pipe.to(device)

# Prompt
prompt = "A cute brown puppy playing with a white kitten in a garden"

# Generate image
image = pipe(prompt).images[0]

# Save image
image.save("output.png")

print("Image saved as output.png")
