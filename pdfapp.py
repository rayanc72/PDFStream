import streamlit as st
import shutil
import os
import subprocess
import plotly.graph_objects as go
import pandas as pd

def modify_cfg_file(cfg_path, background_file, wavelength, dataformat="QA", composition="", qmaxinst=26.5, 
                    qmin=0.0, qmax=20.0, rmin=0.0, rmax=30.0, rstep=0.01, back_scale=1.0, poly=0.9):
    ###Modify the backgroundfile, wavelength, and other parameters in the .cfg file.
    with open(cfg_path, 'r') as file:
        data = file.readlines()

    for i, line in enumerate(data):
        if line.startswith('backgroundfile'):
            data[i] = f"backgroundfile = {background_file}\n"
        if line.startswith('wavelength'):
            data[i] = f"wavelength = {wavelength}\n"
        if line.startswith('dataformat'):
            data[i] = f"dataformat = {dataformat}\n"
        if line.startswith('composition'):
            data[i] = f"composition = {composition}\n"
        if line.startswith('qmaxinst'):
            data[i] = f"qmaxinst = {qmaxinst}\n"
        elif line.startswith('qmin'):
            data[i] = f"qmin = {qmin}\n"
        elif line.startswith('qmax ') or line.startswith('qmax ='):
            data[i] = f"qmax = {qmax}\n"
        elif line.startswith('rmin'):
            data[i] = f"rmin = {rmin}\n"
        elif line.startswith('rmax'):
            data[i] = f"rmax = {rmax}\n"
        elif line.startswith('rstep'):
            data[i] = f"rstep = {rstep}\n"
        elif line.startswith('bgscale'):
            data[i] = f"bgscale = {back_scale}\n"
        elif line.startswith('rpoly'):
            data[i] = f"rpoly = {poly}\n"

    with open(cfg_path, 'w') as file:
        file.writelines(data)

def run_command(command, cwd):
    """Run a system command in a specific directory and return its output and error."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=cwd)
        return result.stdout, result.stderr
    except Exception as e:
        return "", str(e)

def cleanup_temp_dir(tmpdir):
    """Delete the temporary directory if it exists."""
    if os.path.exists(tmpdir):
        shutil.rmtree(tmpdir)
        # st.write(f"Temporary directory {tmpdir} deleted.")


def plot_chi_file(
        data_file: str,
        background_file: str,
        bg_scale: float = 1.0,
        data_color: str = 'blueviolet',
        bg_color: str = 'gray',
        data_width: int = 3,
        bg_width: int = 2,
        bg_dash: str = 'dash'
) -> go.Figure:
    """
    Plot Q vs. I for both sample (data_file) and scaled background (background_file).

    Parameters
    ----------
    data_file : str
        Path to the chi data file (contains '# chi_Q chi_I' header).
    background_file : str
        Path to the background chi file (same format).
    bg_scale : float, default=1.0
        Factor by which to multiply the background intensities.
    data_color : str
        Line color for the sample data.
    bg_color : str
        Line color for the background data.
    data_width : int
        Line width for the sample data.
    bg_width : int
        Line width for the background data.
    bg_dash : str
        Dash style for the background line (e.g., 'dash', 'dot').

    Returns
    -------
    fig : go.Figure
        A Plotly Figure with both traces.
    """

    def _load_chi(path):
        if not os.path.isfile(path):
            raise FileNotFoundError(f"File not found: {path}")
        q_vals, i_vals = [], []
        in_data = False
        with open(path, 'r') as fh:
            for line in fh:
                if line.startswith('#'):
                    if 'chi_Q' in line and 'chi_I' in line:
                        in_data = True
                    continue
                if in_data:
                    parts = line.split()
                    if len(parts) == 2:
                        try:
                            q_vals.append(float(parts[0]))
                            i_vals.append(float(parts[1]))
                        except ValueError:
                            pass
        return q_vals, i_vals

    # Load both datasets
    q_data, i_data = _load_chi(data_file)
    q_bg, i_bg = _load_chi(background_file)
    # Scale the background intensities
    i_bg_scaled = [i * bg_scale for i in i_bg]

    # Build the figure
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=q_data, y=i_data,
        mode='lines',
        name='Sample',
        line=dict(color=data_color, width=data_width)
    ))
    fig.add_trace(go.Scatter(
        x=q_bg, y=i_bg_scaled,
        mode='lines',
        name=f'Background × {bg_scale}',
        line=dict(color=bg_color, width=bg_width, dash=bg_dash)
    ))

    fig.update_layout(
        title='Q vs. I (Sample and Scaled Background)',
        xaxis_title='q (Å⁻¹)',
        yaxis_title='Intensity',
        xaxis_tickfont=dict(size=20, color='black'),
        xaxis_title_font=dict(size=24, color='black'),
        yaxis_tickfont=dict(size=20, color='black'),
        yaxis_title_font=dict(size=24, color='black'),
        legend=dict(font=dict(size=18)),
        template='plotly_white'
    )
    fig.update_layout(
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=0.8,
            xanchor='center',
            x=0.8
        )
    )

    return fig


def plot_gr_file(
    file_path: str,
    marker_size: int   = 6,
    line_width:  int   = 2,
    line_color:  str  = None,
    show_grid:   bool  = True,
    margin:      dict  = None,
):
    """
    Plot two-column data from .gr, .fq or .sq files.
    Automatically sets:
      • x/y axis labels
      • plot & dataframe titles
      • default line color
    based on the extension of file_path.
    """

    # 1) Verify file exists
    if not os.path.isfile(file_path):
        st.error(f"File not found: {file_path}")
        return

    # 2) Decide labels & defaults by extension
    ext = os.path.splitext(file_path)[1].lower()
    settings = {
        '.gr': {'x':'r (Å)',        'y':'G(r) (1/Å²)',  'title':'r vs. G(r)',  'color':'firebrick'},
        '.fq': {'x':'q (Å⁻¹)',       'y':'F(q) (1/Å)',    'title':'q vs. F(q)',  'color':'darkslategrey'},
        '.sq': {'x':'q (Å⁻¹)',       'y':'S(a.u.)',       'title':'q vs. S(a.u.)','color':'darkslategrey'},
    }.get(ext)

    if settings is None:
        st.warning(f"Unknown extension '{ext}', defaulting to .gr settings.")
        settings = {'x':'r (Å)', 'y':'G(r) (1/Å²)', 'title':'r vs. G(r)', 'color':'salmon'}

    x_label = settings['x']
    y_label = settings['y']
    title   = settings['title']
    default_color = settings['color']
    color = line_color or default_color

    # 3) Read the “#### start data” block
    xs, ys = [], []
    in_data = False
    with open(file_path, 'r') as fh:
        for line in fh:
            if line.startswith('#### start data'):
                in_data = True
                continue
            if in_data and line.startswith('####'):
                break
            if in_data and not line.startswith('#'):
                parts = line.split()
                if len(parts) == 2:
                    try:
                        xs.append(float(parts[0]))
                        ys.append(float(parts[1]))
                    except ValueError:
                        continue

    if not xs:
        st.warning(f"No numeric data found in the '#### start data' section of {os.path.basename(file_path)}.")
        return

    # 4) Show raw data
    # df = pd.DataFrame({x_label: xs, y_label: ys})
    # with st.expander(f"{title} data"):
    #     st.dataframe(df, hide_index=True, use_container_width=True)

    # 5) Configure margins
    if margin is None:
        margin = dict(l=60, r=20, t=60, b=60)

    # 6) Build Plotly figure
    fig = go.Figure(
        data=go.Scatter(
            x=xs,
            y=ys,
            mode='lines+markers',
            name=title,
            line=dict(color=color, width=line_width),
            marker=dict(size=marker_size),
        )
    )
    fig.update_layout(
        title=title,
        xaxis_title=x_label,
        yaxis_title=y_label,
        template='plotly_white',
        xaxis=dict(showgrid=show_grid, tickfont=dict(size=20, color='black'), title_font=dict(size=24, color='black')),
        yaxis=dict(showgrid=show_grid, tickfont=dict(size=20, color='black'), title_font=dict(size=24, color='black')),
        margin=margin,
    )

    st.plotly_chart(fig, use_container_width=True)



if "upload_counter" not in st.session_state:
    st.session_state["upload_counter"] = 0


def main():
    st.set_page_config(layout="wide") 
    st.title(":red[PDF] Processor")

    # Create a persistent temporary directory in the current working directory
    tmpdir = os.path.join(os.getcwd(), "pdfgetx3_temp")

    # Upload data and background files
    col_d, col_b = st.columns(2, gap="large")
    with col_d:
        data_files = st.file_uploader(
            "Upload Data Files (.chi)",
            type="chi",
            accept_multiple_files=True,
            key=f"data_uploader_{st.session_state['upload_counter']}"
        )

        if "saved_paths" not in st.session_state:
            st.session_state["saved_paths"] = []
        upload_dir = os.path.join(os.getcwd(), "data_chi_files")
        os.makedirs(upload_dir, exist_ok=True)
        saved_paths = []
        if data_files:
            for uf in data_files:
                dst = os.path.join(upload_dir, uf.name)
                with open(dst, "wb") as f:
                    f.write(uf.getbuffer())
                saved_paths.append(dst)
        st.session_state["saved_paths"] = saved_paths
    with col_b:
        background_file = st.file_uploader("Upload Background File (.chi)", type="chi")

    filenames = [os.path.basename(p) for p in st.session_state["saved_paths"]]
    if filenames:
        selected_name = st.selectbox("Choose data file", filenames, key="selected_name")
        data_file = os.path.join(upload_dir, selected_name)
    else:
        st.info("Please upload and select a data file.")
        data_file = None

    def clear_uploads(upload_dir=upload_dir):
        # remove files from disk
        for fname in os.listdir(upload_dir):
            os.remove(os.path.join(upload_dir, fname))
        # clear saved paths and selection
        st.session_state["saved_paths"] = []
        if "selected_name" in st.session_state:
            del st.session_state["selected_name"]
        # bump the counter to reset the uploader
        st.session_state["upload_counter"] += 1



    st.divider()
    composition = st.text_input("Composition (e.g., C6NH8)", value="C8N2H22PbI6")


    with st.expander('Additional parameters'):
        dataformat = st.selectbox("Select Data Format", options=["twotheta", "QA", "Qnm"], index=1)
        rstep = st.number_input("rstep", min_value=0.001, value=0.01)
        wavelength = st.text_input("Enter Wavelength Value", "0.1665")
        qmaxinst = st.number_input("Q Max intensity", min_value=0.0, value=26.5)


    col5, col6 = st.columns(2, gap="large")

    with col5:
        qmin, qmax = st.slider("Select q range", 0.0, 100.0, (0.6, 20.0))
        poly = st.slider("rpoly", min_value=0.01, max_value=10.0, value=0.9)
    
    with col6:
        rmin, rmax = st.slider("Select r range", 0.0, 40.0, (0.0, 30.0))
        # back_scale = st.number_input("Background scale", min_value=0.01, value=1.0)
        back_scale = st.slider("Background scale", min_value=0.1, max_value=10.0, value=1.0)


    st.divider()



    # Ensure that files have been uploaded and composition is provided
    if data_file and background_file and wavelength and composition:
        if st.button("Run", use_container_width=True, type="primary", icon="👊️"):
            cleanup_temp_dir(tmpdir)  # Clean previous run's temp directory
            
            # Create the temporary directory
            if not os.path.exists(tmpdir):
                os.makedirs(tmpdir)

            # Save uploaded files to the temporary directory
            data_file_path = os.path.join(tmpdir, selected_name)
            background_file_path = os.path.join(tmpdir, background_file.name)

            # with open(data_file_path, 'wb') as df:
            #     df.write(data_file.read())
            shutil.copyfile(data_file, data_file_path)

            with open(background_file_path, 'wb') as bf:
                bf.write(background_file.read())


            # Plot the data file
            with st.expander('Q vs I plot', expanded=True):
                fig = plot_chi_file(
                         data_file=data_file_path,
                         background_file=background_file_path,
                         bg_scale=back_scale
                            )
                st.plotly_chart(fig, use_container_width=True)


            # Copy pdfgetx3.cfg to the temporary directory
            cfg_file_src = os.path.join(os.getcwd(), 'pdfgetx3.cfg')
            cfg_file_dest = os.path.join(tmpdir, 'pdfgetx3.cfg')
            shutil.copy(cfg_file_src, cfg_file_dest)

            # Modify the configuration file with the additional parameters
            modify_cfg_file(cfg_file_dest, background_file.name, wavelength, dataformat, composition, qmaxinst, qmin, qmax, rmin, rmax, rstep, back_scale, poly)

            # Run the command: pdfgetx3 <datafile> from inside the temp directory
            command = f"pdfgetx3 {data_file_path}"
            # st.write(f"Running command: `{command}` from directory: {tmpdir}")
                

            # Capture the output and error of the command
            stdout, stderr = run_command(command, cwd=tmpdir)

            # Display the command output and error on the app page
            if stdout:
                st.text_area("Command Output:", stdout)
            if stderr:
                st.text_area("Command Error:", stderr)

            output_file_path_gr = data_file_path.replace('.chi', '.gr')
            output_file_path_sq = data_file_path.replace('.chi', '.sq')
            output_file_path_fq = data_file_path.replace('.chi', '.fq')
            if os.path.exists(output_file_path_gr):
                with st.expander('S(q) and F(q) plots'):
                    col7, col8 = st.columns(2)
                    with col7:
                        with open(output_file_path_fq, 'rb') as f:
                            # Plot the .gr file
                            plot_gr_file(output_file_path_fq)
                            if st.download_button('Download .fq File', f, file_name=os.path.basename(output_file_path_fq), icon="⤵️"):
                                # Delete the temporary directory after download
                                pass
                    with col8:
                        with open(output_file_path_sq, 'rb') as f:
                            # Plot the .gr file
                            plot_gr_file(output_file_path_sq)
                            if st.download_button('Download .sq File', f, file_name=os.path.basename(output_file_path_sq), icon="⤵️"):
                                # Delete the temporary directory after download
                                pass
                with open(output_file_path_gr, 'rb') as f:
                    col9, col10, col11 = st.columns([1,10,1])
                    # Plot the .gr file
                    with col10:
                        plot_gr_file(output_file_path_gr)
                        if st.download_button('Download .gr File', f, file_name=os.path.basename(output_file_path_gr), icon="⤵️"):
                            # Delete the temporary directory after download
                            pass

            else:
                st.error(f"Failed to generate the .gr file. Check the contents of {tmpdir} for debugging.")

    else:
        st.warning("Please upload both files, provide composition, and input a valid wavelength value.")

    st.button("Clear uploaded data files", on_click=clear_uploads, icon="⚠️️️")




if __name__ == "__main__":
    main()