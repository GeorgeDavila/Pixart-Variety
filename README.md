# PixArt-alpha with variable model and T5 encoder input and Cog Cloud Deployment

This is an implementation of [PixArt-alpha/PixArt-XL-2-1024-MS](https://huggingface.co/PixArt-alpha/PixArt-XL-2-1024-MS) as a [Cog](https://github.com/replicate/cog) model. Cog deployment code based on lucataco's Pixart repo https://github.com/lucataco/cog-pixart-xl-2



# Cog Deployment 
This repo is largely intended to test out various Pixart model variants in one repo as well as allow us to quickly test out new Pixart variants on replicate without needing to push a new deployment. 

For the deployment of a variant you actually want to use in production it is best to host a dedicated deployment in the style of https://github.com/lucataco/cog-pixart-xl-2 to allow your model variant to be loaded into memory (saving you time and money). 


# Example

![alt text](output.0.png)
