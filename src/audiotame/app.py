import os
import subprocess
import sys
import time

try:
    import gradio as gr
    os.environ["GRADIO_ANALYTICS_ENABLED"] = "False"
    os.environ["GRADIO_RUNNING"] = "1"
    
except:
    print("Could not load Gradio module")
    sys.exit(0)


def set_env(
    DB_PEAK_BEFORE_ALL="-100", DB_PEAK_AFTER_NORM="-100",NORM_TYPE="ebu", LOUD_TARGET="-21", ARNNDN="0", ARNNDN_MODEL="cb.rnnn", 
    SOX_DENOISE="1", SOX_FACTOR="0.21", SOX_NOISE_THRESHOLD="-50", SOX_NOISE_MIN_DURATION="0.5", REGULAR_DENOISE=1, REGULAR_NOISE_THRESHOLD="-50", SILENCE_FLOOR="-60", DEBUG="0"):

    for key, value in locals().items():
        
        hold_value = value

        if hold_value == True:
            hold_value = 1
        elif hold_value == False:
            hold_value = 0

        os.environ[key] = str(hold_value)
    
    print("env has been set")


def tame(audio):

    if audio is None:
        return "No audio provided!"
    

    abs_dir_name = os.path.dirname(audio)
    basename = os.path.basename(audio)
    name, ext = os.path.splitext(basename)
    file_output = f"{name}-tamed{ext}"
    out_file = f"{abs_dir_name}/{file_output}"
    out_file = remove_whitespace(out_file)

    input_stats = stats(audio)

    if os.getenv("NORM_TYPE") == None:
        print("Environment not yet set. Running set_env function.")
        set_env()

    command = ["audiotame", str(audio)]
    result = subprocess.run(command, capture_output=True, text=True)
    print(result.stderr)
    print(result.stdout)
    
    tamed_stats = stats(out_file)
    return input_stats, out_file, tamed_stats


def acx(input):
    command = ["audiotame", str(input), "acx"]
    result = subprocess.run(command, capture_output=True, text=True)
    return result.stdout


def stats(input):
    command = ["audiotame", str(input), "stats"]
    result = subprocess.run(command, capture_output=True, text=True)
    return result.stdout

def convert(input, format):

    if input == None:
        return None

    command = ["audiotame", str(input), "convert", format]
    result = subprocess.run(command, check=True)
    
    abs_dir_name = os.path.dirname(input)
    basename = os.path.basename(input)
    name, ext = os.path.splitext(basename)
    file_output = f"{name}.{format}"
    out_file = f"{abs_dir_name}/{file_output}"
    out_file = remove_whitespace(out_file)

    return out_file


def remove_whitespace(input):
    
    str_input = str(input)
    if " " in str_input:
        out = str_input.replace(" ", "")
    else:
        out = input
    
    return out


with gr.Blocks() as tameblock:
    
    with gr.Row(equal_height=True):
        audiofile = gr.Audio(sources=["upload"], type="filepath", label="Input Audio")
        tamed_audiofile=gr.Audio(label="Tamed Audio", show_download_button=True)

    with gr.Row(equal_height=True, visible=False) as statsrow:
        input_stats_out=gr.Code(label="Input Stats", lines=5, max_lines=6)
        tamed_stats_out=gr.Code(label="Tamed Stats", lines=5, max_lines=6)
    
    def update_dummy():
        return str(time.time())

    dummy = gr.Textbox(value=str(time.time()), visible=False)
    

    tamebtn = gr.Button("Tame", variant="primary", size="lg")

    def showstats():
        return { statsrow: gr.Column(visible=True) }
    
    def hidestats():
        return { statsrow: gr.Column(visible=False) }

    def clear_tame():
        return None, None, None

    gr.on(
        triggers=[tamebtn.click],
        fn=clear_tame,
        inputs=None,
        outputs=[input_stats_out, tamed_audiofile, tamed_stats_out]
    ).then(fn=update_dummy, inputs=None, outputs=dummy
    ).then(hidestats, inputs=None, outputs=statsrow
    ).then(tame, inputs=audiofile, outputs=[input_stats_out, tamed_audiofile, tamed_stats_out]
    ).then(showstats, inputs=None, outputs=statsrow)

    #tamebtn.click(fn=tame, inputs=audiofile, outputs=[input_stats_out, tamed_audiofile, tamed_stats_out])



with gr.Blocks() as envars:
    with gr.Row():
        DB_PEAK_BEFORE_ALL = gr.Slider(value="-100", minimum=-100, maximum=10, step=1, label="dB Peak before all functions (-100 means this is disabled)")
        DB_PEAK_AFTER_NORM =  gr.Slider(value="-100", minimum=-100, maximum=10, step=1, label="dB Peak after normalization (-100 means this is disabled)")

    with gr.Row():
        NORM_TYPE = gr.Radio(["ebu", "rms"], label="Normalization Type", value="ebu")
        LOUD_TARGET = gr.Slider(value="-21", minimum=-80, maximum=0, step=1, label="Loudness Normalization Target")

    with gr.Row():
        ARNNDN = gr.Checkbox(
                label="ARNNDN", 
                value=0, 
                info="""RNN are models trained on noise sound. It will try to identify noise in your audio and remove it. If your audio sounds muffled in some parts after passing through audiotame, disable this option"""
            )

        ARNNDN_MODEL = gr.Radio(["bd.rnnn", "cb.rnnn", "lq.rnnn", "mp.rnnn", "sh.rnnn", "std.rnnn"], value="cb.rnnn", label="RNN Models")

    with gr.Row():
        with gr.Column():
            SOX_DENOISE = gr.Checkbox(
                    label="SOX_DENOISE", 
                    value=1, 
                    info="""Enable denoising by sox"""
                )

            SOX_FACTOR =  gr.Slider(
                    label="SOX_FACTOR", 
                    value=0.21, minimum=0, maximum=1, step=0.01, 
                    info="""The factor that sox will use to denoise your audio. 0 is none, 1 is maximum. best values are regarded to be in 0.2-0.3 range"""
                )

            SOX_NOISE_THRESHOLD =  gr.Slider(
                    label="SOX_NOISE_THRESHOLD", 
                    value=-50, minimum=-100, maximum=0, step=1,
                    info="""The dB value that sets a threshold below which sound is considered noise by sox."""
                )



            SOX_NOISE_MIN_DURATION = gr.Slider(
                    label="SOX_NOISE_MIN_DURATION",
                    value=0.5, minimum=0, maximum=10, step=0.01,
                    info="""The minimum duration that a sound below the threshold needs to be considered noise."""
                )

        with gr.Column():
            REGULAR_DENOISE = gr.Checkbox(
                label = "REGULAR_DENOISE",
                value = 1,
                info = """Enable regular denoise (lowers intensity below a threshold)"""
            )

            REGULAR_NOISE_THRESHOLD = gr.Slider(
                label="REGULAR_NOISE_THRESHOLD",
                value = -50, minimum=-80, maximum=-20, step=1,
                info = """The dB value that sets a threshold below which sound is considered noise. Audio below this will be lowered"""
            )

            SILENCE_FLOOR = gr.Slider(
                    label="SILENCE_FLOOR",
                    value=-60, minimum=-100, maximum=0, step=1,
                    info="""The dB value that sets a threshold below which sound is considered silence."""
                )

    DEBUG = gr.Checkbox(label="DEBUG", value=0, info="Will print stats at each step on the console")


    gr.on(
        fn=set_env,
        inputs=[
            DB_PEAK_BEFORE_ALL, DB_PEAK_AFTER_NORM, NORM_TYPE, LOUD_TARGET, ARNNDN, ARNNDN_MODEL, 
            SOX_DENOISE, SOX_FACTOR, SOX_NOISE_THRESHOLD, SOX_NOISE_MIN_DURATION, 
            REGULAR_DENOISE, REGULAR_NOISE_THRESHOLD, SILENCE_FLOOR, DEBUG
        ],
        outputs=None
    )


with gr.Blocks() as convertblock:
    with gr.Row(equal_height=True):
        audiofile = gr.Audio(sources="upload", type="filepath", label="Input Audio")
        converted_audio = gr.Audio(label="Converted Audio", show_download_button=True)

    format = gr.Radio(["wav", "flac", "mp3", "m4b", "aac", "ogg", "wma", "aiff", "webm"], label="Convert to:")

    convert_btn = gr.Button("Convert", variant="primary")
    convert_btn.click(fn=convert, inputs=[audiofile, format], outputs=converted_audio)

    def clear_convert():
        return None

    gr.on(
        triggers=[convert_btn.click],
        fn=convert, inputs=[audiofile, format], outputs=converted_audio)
    

with gr.Blocks() as statsblock:
            
    audiofile = gr.Audio(sources="upload", type="filepath", label="Input Audio")

    with gr.Row(equal_height=True):
        statsout = gr.Code(label="Stats", lines=5, max_lines=6)
        acxout = gr.Code(label="ACX", lines=5, max_lines=6)

    with gr.Row(equal_height=True):

        statsbtn = gr.Button("Stats", variant="primary")
        statsbtn.click(stats, audiofile, statsout)
        acxbtn = gr.Button("ACX", variant="primary")
        acxbtn.click(acx, audiofile, acxout)


with gr.Blocks() as main:
    tameblock.render() 
    envars.render()  


demo = gr.TabbedInterface(
    interface_list=[main, convertblock, statsblock],
    tab_names=["Tame", "Convert", "Stats/ACX"],
    title="AudioTame",
    theme=gr.themes.Default(text_size="sm", spacing_size="sm", font=["ui-system", "Arial", "sans-serif", "monospace"])

)

gradio_server = os.getenv("GRADIO_SERVER_NAME")
if gradio_server != "0.0.0.0":
    gradio_server="127.0.0.1"


demo.queue(default_concurrency_limit=2)

try:
    demo.launch(share=False, server_name=gradio_server, pwa=True)
except KeyboardInterrupt:
    print("Shutting down...")
    sys.exit(0)