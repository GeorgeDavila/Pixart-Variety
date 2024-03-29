# Prediction interface for Cog ⚙️
# https://github.com/replicate/cog/blob/main/docs/python.md

from cog import BasePredictor, Input, Path
import os
import torch
from typing import List
from diffusers import (
    PixArtAlphaPipeline,
    DDIMScheduler,
    DPMSolverMultistepScheduler,
    EulerAncestralDiscreteScheduler,
    EulerDiscreteScheduler,
    HeunDiscreteScheduler,
    PNDMScheduler,
)
from transformers import T5EncoderModel

class KarrasDPM:
    def from_config(config):
        return DPMSolverMultistepScheduler.from_config(config, use_karras_sigmas=True)

#MODEL_NAME = "PixArt-alpha/PixArt-XL-2-1024-MS"
MODEL_CACHE = "model-cache"

SCHEDULERS = {
    "DDIM": DDIMScheduler,
    "DPMSolverMultistep": DPMSolverMultistepScheduler,
    "HeunDiscrete": HeunDiscreteScheduler,
    "KarrasDPM": KarrasDPM,
    "K_EULER_ANCESTRAL": EulerAncestralDiscreteScheduler,
    "K_EULER": EulerDiscreteScheduler,
    "PNDM": PNDMScheduler,
}

style_list = [
    {
        "name": "None",
        "prompt": "{prompt}",
        "negative_prompt": "",
    },
    {
        "name": "Cinematic",
        "prompt": "cinematic still {prompt} . emotional, harmonious, vignette, highly detailed, high budget, bokeh, cinemascope, moody, epic, gorgeous, film grain, grainy",
        "negative_prompt": "anime, cartoon, graphic, text, painting, crayon, graphite, abstract, glitch, deformed, mutated, ugly, disfigured",
    },
    {
        "name": "Photographic",
        "prompt": "cinematic photo {prompt} . 35mm photograph, film, bokeh, professional, 4k, highly detailed",
        "negative_prompt": "drawing, painting, crayon, sketch, graphite, impressionist, noisy, blurry, soft, deformed, ugly",
    },
    {
        "name": "Anime",
        "prompt": "anime artwork {prompt} . anime style, key visual, vibrant, studio anime,  highly detailed",
        "negative_prompt": "photo, deformed, black and white, realism, disfigured, low contrast",
    },
    {
        "name": "Manga",
        "prompt": "manga style {prompt} . vibrant, high-energy, detailed, iconic, Japanese comic style",
        "negative_prompt": "ugly, deformed, noisy, blurry, low contrast, realism, photorealistic, Western comic style",
    },
    {
        "name": "Digital Art",
        "prompt": "concept art {prompt} . digital artwork, illustrative, painterly, matte painting, highly detailed",
        "negative_prompt": "photo, photorealistic, realism, ugly",
    },
    {
        "name": "Pixel art",
        "prompt": "pixel-art {prompt} . low-res, blocky, pixel art style, 8-bit graphics",
        "negative_prompt": "sloppy, messy, blurry, noisy, highly detailed, ultra textured, photo, realistic",
    },
    {
        "name": "Fantasy art",
        "prompt": "ethereal fantasy concept art of  {prompt} . magnificent, celestial, ethereal, painterly, epic, majestic, magical, fantasy art, cover art, dreamy",
        "negative_prompt": "photographic, realistic, realism, 35mm film, dslr, cropped, frame, text, deformed, glitch, noise, noisy, off-center, deformed, cross-eyed, closed eyes, bad anatomy, ugly, disfigured, sloppy, duplicate, mutated, black and white",
    },
    {
        "name": "Neonpunk",
        "prompt": "neonpunk style {prompt} . cyberpunk, vaporwave, neon, vibes, vibrant, stunningly beautiful, crisp, detailed, sleek, ultramodern, magenta highlights, dark purple shadows, high contrast, cinematic, ultra detailed, intricate, professional",
        "negative_prompt": "painting, drawing, illustration, glitch, deformed, mutated, cross-eyed, ugly, disfigured",
    },
    {
        "name": "3D Model",
        "prompt": "professional 3d model {prompt} . octane render, highly detailed, volumetric, dramatic lighting",
        "negative_prompt": "ugly, deformed, noisy, low poly, blurry, painting",
    },
]

def apply_style(style, prompt, negative_prompt):
    if style == "None":
        return prompt, negative_prompt
    else:
        for style_dict in style_list:
            if style_dict["name"] == style:
                return style_dict["prompt"].format(prompt=prompt), style_dict["negative_prompt"]

class Predictor(BasePredictor):
    def setup(self) -> None:
        """sacrifice preloading efficiency for some customizability, see README"""
        pass 

    @torch.inference_mode()
    def predict(
        self,
        prompt: str = Input(description="Input prompt", default="A cat doing karate in Madrid, cinematic, 8k UHD"),
        negative_prompt: str = Input(description="Negative prompt", default=None),
        modelChoice: str = Input(
            description="Pixart model to use",
            choices=["PixArt-alpha/PixArt-XL-2-1024-MS", "PixArt-alpha/PixArt-LCM-XL-2-1024-MS", "PixArt-alpha/PixArt-XL-2-512x512"],
            default="PixArt-alpha/PixArt-XL-2-1024-MS",
        ),
        useCustomModel: bool = Input(
            description="Enter custom model - check this to use the Pixart model you type in below rather than one of the choices above.",
            default=False
        ),
        customModel: str = Input(
            description="Custom Pixart model path (from huggingface hub)",
            default="PixArt-alpha/PixArt-XL-2-1024-MS",
        ),
        textEncoderChoice: str = Input(
            description="Text Encoder for Pixart model to use",
            choices=["PixArt-alpha/PixArt-XL-2-1024-MS", "PixArt-alpha/PixArt-LCM-XL-2-1024-MS", "PixArt-alpha/PixArt-XL-2-512x512"],
            default="PixArt-alpha/PixArt-XL-2-1024-MS",
        ),
        useCustomTextEncoder: bool = Input(
            description="Enter custom text encoder - check this to use the text encoder you type in below rather than one of the choices above.",
            default=False
        ),
        customTextEncoder: str = Input(
            description="Custom text encoder path (from huggingface hub)",
            default="PixArt-alpha/PixArt-XL-2-1024-MS",
        ),
        style: str = Input(
            description="Image style",
            choices=["None", "Cinematic", "Photographic", "Anime", "Manga", "Digital Art", "Pixel Art", "Fantasy Art", "Neonpunk", "3D Model"],
            default="None",
        ),
        width: int = Input(
            description="Width of output image",
            default=1024,
        ),
        height: int = Input(
            description="Height of output image",
            default=1024,
        ),
        num_outputs: int = Input(
            description="Number of images to output.",
            ge=1,
            le=4,
            default=1,
        ),
        scheduler: str = Input(
            description="scheduler",
            choices=SCHEDULERS.keys(),
            default="DPMSolverMultistep",
        ),
        num_inference_steps: int = Input(
            description="Number of denoising steps", ge=1, le=100, default=14
        ),
        guidance_scale: float = Input(
            description="Scale for classifier-free guidance", ge=1, le=50, default=4.5
        ),
        seed: int = Input(
            description="Random seed. Leave blank to randomize the seed", default=None
        ),
    ) -> List[Path]:
        """Run a single prediction on the model"""

        if useCustomModel:
            modelChoice = customModel
        if useCustomTextEncoder:
            textEncoderChoice = customTextEncoder

        #----------------- Model Setup Start -----------------
        text_encoder = T5EncoderModel.from_pretrained(
            textEncoderChoice,
            subfolder="text_encoder",
            load_in_8bit=True,
            device_map="auto",
        )
        pipe = PixArtAlphaPipeline.from_pretrained(
            modelChoice,
            text_encoder=text_encoder,
            torch_dtype=torch.float16,
            use_safetensors=True,
            #cache_dir=MODEL_CACHE
        )
        # speed-up T5
        pipe.text_encoder.to_bettertransformer()
        self.pipe = pipe.to("cuda")
        #----------------- Model Setup End -----------------


        if seed is None:
            seed = int.from_bytes(os.urandom(4), "big")
        print(f"Using seed: {seed}")
        generator = torch.Generator("cuda").manual_seed(seed)

        self.pipe.scheduler = SCHEDULERS[scheduler].from_config(self.pipe.scheduler.config)

        prompt, negative_prompt = apply_style(style, prompt, negative_prompt)
        print("Prompt:", prompt, " Negative Prompt:", negative_prompt)
        output = self.pipe(
            prompt=prompt,
            negative_prompt=negative_prompt,
            width=width,
            height=height,
            guidance_scale=guidance_scale,
            num_inference_steps=num_inference_steps,
            generator=generator,
            num_images_per_prompt=num_outputs,
            output_type="pil",
        )

        output_paths = []
        for i, img in enumerate(output.images):
            output_path = f"/tmp/out-{i}.png"
            img.save(output_path)
            output_paths.append(Path(output_path))

        return output_paths