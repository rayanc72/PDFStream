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

def plot_chi_file(file_path):
    """Plot Q vs. I from the chi data file using Plotly graph_objects and display the DataFrame."""
    q_values = []
    i_values = []

    with open(file_path, 'r') as file:
        lines = file.readlines()

    # # Debug: Print first few lines of the file to verify
    # st.write("File Content Preview:")
    # st.write(lines[:10])

    # Flag to indicate when to start reading data
    data_section = False

    for line in lines:
        # Skip header lines starting with '#'
        if line.startswith('#'):
            if "chi_Q" in line and "chi_I" in line:
                # Start of the data section
                data_section = True
            continue

        # Parse data lines
        if data_section:
            parts = line.split()
            if len(parts) == 2:
                try:
                    q = float(parts[0])
                    i = float(parts[1])
                    q_values.append(q)
                    i_values.append(i)
                except ValueError:
                    continue

    # Debug: Print collected data
    # st.write("Collected Data:")
    # st.write(f"Q values: {q_values[:10]}")
    # st.write(f"I values: {i_values[:10]}")

    # Convert to a pandas DataFrame
    df = pd.DataFrame({'Q': q_values, 'I': i_values})

    # Debug: Print DataFrame head
    # st.write("DataFrame Preview:")
    # st.write(df.head())  # Display the first few rows of the DataFrame

    # Create a plot using Plotly graph_objects
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['Q'], y=df['I'], mode='lines', name='Intensity',line=dict(color='blueviolet', width=3)))
    fig.update_layout(title='Q vs. I',
                      xaxis_title='Q (1/Å)',
                      xaxis_tickfont=dict(size=20, color='black'),
                      xaxis_title_font=dict(size=24, color='black'),
                      yaxis_title='Intensity',
                      yaxis_tickfont=dict(size=20, color='black'),
                      yaxis_title_font=dict(size=24, color='black'),
                      showlegend=False)
    
    return fig



def plot_gr_file(file_path):
    """Plot r vs. G(r) from the .gr file data section using Plotly."""
    r_values = []
    g_values = []

    with open(file_path, 'r') as file:
        lines = file.readlines()


    # Flag to identify the start of the data section
    data_section = False

    for line in lines:
        # Start of the data section
        if line.startswith('#### start data'):
            data_section = True
            continue
        
        # End of the data section
        if data_section and line.startswith('####'):
            break
        
        # Parse data lines
        if data_section and not line.startswith('#'):
            parts = line.split()
            if len(parts) == 2:
                try:
                    r = float(parts[0])
                    g = float(parts[1])
                    r_values.append(r)
                    g_values.append(g)
                except ValueError:
                    continue
    # Convert to a pandas DataFrame
    df = pd.DataFrame({'r': r_values, 'G(r)': g_values})

    with st.expander('r vs. G(r) data'):
        st.dataframe(df, hide_index=True, use_container_width=True)

    # Create a Plotly plot
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=r_values, y=g_values, mode='lines+markers', name='G(r)', line=dict(color='salmon')))
    fig.update_layout(
        title='r vs. G(r)',
        xaxis_title='r (Å)',
        yaxis_title='G(r) (1/Å^2)',
        template='plotly_white',
        xaxis_tickfont=dict(size=20, color='black'),
        xaxis_title_font=dict(size=24, color='black'),
        yaxis_tickfont=dict(size=20, color='black'),
        yaxis_title_font=dict(size=24, color='black')
    )

    st.plotly_chart(fig, use_container_width=True)

def main():
    st.set_page_config(layout="wide") 
    st.title(":red[PDF] Processor")

    # Create a persistent temporary directory in the current working directory
    tmpdir = os.path.join(os.getcwd(), "pdfgetx3_temp")

    # Upload data and background files
    data_file = st.file_uploader("Upload Data File (.chi)", type="chi")
    background_file = st.file_uploader("Upload Background File (.chi)", type="chi")
    wavelength = st.text_input("Enter Wavelength Value", "0.1665")

    # Additional input fields for the new parameters
    
    composition = st.text_input("Composition (e.g., C6NH8)")
    dataformat = st.selectbox("Select Data Format", options=["twotheta", "QA", "Qnm"], index=1)
    qmaxinst = st.number_input("Q Max intensity", min_value=0.0, value=26.5)
    back_scale=st.number_input("Background scale", min_value=0.01, value=1.0)
    poly=st.number_input("rpoly", min_value=0.01, value=0.9)

    col1, col2 = st.columns(2)

    with col1:
        
        qmin = st.number_input("Q range min", min_value=0.0, value=0.6)
        rmin = st.number_input("r range min", min_value=0.0, value=0.0)
    
    with col2:
        qmax = st.number_input("Q range max", min_value=0.0, value=20.0)
        rmax = st.number_input("r range max", min_value=0.0, value=30.0)
    
    rstep = st.number_input("rstep", min_value=0.001, value=0.01)

    # Ensure that files have been uploaded and composition is provided
    if data_file and background_file and wavelength and composition:
        if st.button("Run"):
            cleanup_temp_dir(tmpdir)  # Clean previous run's temp directory
            
            # Create the temporary directory
            if not os.path.exists(tmpdir):
                os.makedirs(tmpdir)

            # Save uploaded files to the temporary directory
            data_file_path = os.path.join(tmpdir, data_file.name)
            background_file_path = os.path.join(tmpdir, background_file.name)

            with open(data_file_path, 'wb') as df:
                df.write(data_file.read())

            with open(background_file_path, 'wb') as bf:
                bf.write(background_file.read())


            # Plot the data file
            fig = plot_chi_file(data_file_path)
            st.plotly_chart(fig, use_container_width=True)


            # Copy pdfgetx3.cfg to the temporary directory
            cfg_file_src = os.path.join(os.getcwd(), 'pdfgetx3.cfg')
            cfg_file_dest = os.path.join(tmpdir, 'pdfgetx3.cfg')
            shutil.copy(cfg_file_src, cfg_file_dest)

            # Modify the configuration file with the additional parameters
            modify_cfg_file(cfg_file_dest, background_file.name, wavelength, dataformat, composition, qmaxinst, qmin, qmax, rmin, rmax, rstep, back_scale, poly)

            # Run the command: pdfgetx3 <datafile> from inside the temp directory
            command = f"pdfgetx3 {data_file.name}"
            # st.write(f"Running command: `{command}` from directory: {tmpdir}")
                

            # Capture the output and error of the command
            stdout, stderr = run_command(command, cwd=tmpdir)

            # Display the command output and error on the app page
            if stdout:
                st.text_area("Command Output:", stdout)
            if stderr:
                st.text_area("Command Error:", stderr)

            # Check for the output .gr file in the temp directory
            output_file_path = os.path.join(tmpdir, data_file.name.replace('.chi', '.gr'))
            if os.path.exists(output_file_path):
                # Provide download option
                with open(output_file_path, 'rb') as f:
                    # Plot the .gr file
                    plot_gr_file(output_file_path)
                    if st.download_button('Download .gr File', f, file_name=os.path.basename(output_file_path)):
                        # Delete the temporary directory after download
                        cleanup_temp_dir(tmpdir)
            else:
                st.error(f"Failed to generate the .gr file. Check the contents of {tmpdir} for debugging.")

    else:
        st.warning("Please upload both files, provide composition, and input a valid wavelength value.")

if __name__ == "__main__":
    main()