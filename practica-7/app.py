import os

import gradio as gr
import torch
from transformers import AutoImageProcessor, AutoModelForImageClassification

MODELO = "google/mobilenet_v2_1.0_224"

# Se carga una sola vez al iniciar la app
procesador = AutoImageProcessor.from_pretrained(MODELO)
modelo = AutoModelForImageClassification.from_pretrained(MODELO)
modelo.eval()


def clasificar(imagen):
    """Regresa las 3 etiquetas más probables con su porcentaje."""
    if imagen is None:
        return {}

    entradas = procesador(images=imagen.convert("RGB"), return_tensors="pt")
    with torch.no_grad():
        logits = modelo(**entradas).logits

    probabilidades = torch.softmax(logits, dim=-1)[0]
    top = torch.topk(probabilidades, k=3)

    return {
        modelo.config.id2label[i.item()]: p.item()
        for p, i in zip(top.values, top.indices)
    }


carpeta_ejemplos = os.path.join(os.path.dirname(__file__), "ejemplos")
ejemplos = [
    [os.path.join(carpeta_ejemplos, f)]
    for f in sorted(os.listdir(carpeta_ejemplos))
] if os.path.isdir(carpeta_ejemplos) else None

demo = gr.Interface(
    fn=clasificar,
    inputs=gr.Image(type="pil", label="Imagen"),
    outputs=gr.Label(num_top_classes=3, label="Top 3"),
    title="Clasificador de imágenes",
    description=f"Modelo: {MODELO}. Sube una imagen y obtén las 3 etiquetas más probables.",
    examples=ejemplos,
)

if __name__ == "__main__":
    demo.launch(share=True)
