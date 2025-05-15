import streamlit as st
import pandas as pd
import zipfile
import io
import time
import tempfile

COLUNAS_ESTABELE = [
    'CNPJ_BASICO', 'CNPJ_ORDEM', 'CNPJ_DV', 'IDENTIFICADOR_MATRIZ_FILIAL',
    'NOME_FANTASIA', 'SITUACAO_CADASTRAL', 'DATA_SITUACAO_CADASTRAL',
    'MOTIVO_SITUACAO_CADASTRAL', 'NOME_CIDADE_EXTERIOR', 'PAIS',
    'DATA_INICIO_ATIVIDADE', 'CNAE_FISCAL_PRINCIPAL', 'CNAE_FISCAL_SECUNDARIA',
    'TIPO_LOGRADOURO', 'LOGRADOURO', 'NUMERO', 'COMPLEMENTO', 'BAIRRO', 'CEP',
    'UF', 'MUNICIPIO', 'DDD1', 'TELEFONE1', 'DDD2', 'TELEFONE2', 'DDD_FAX',
    'FAX', 'EMAIL', 'SITUACAO_ESPECIAL', 'DATA_SITUACAO_ESPECIAL'
]

st.title("Conversor de Arquivo .ESTABELE para CSV UTF-8")

uploaded_file = st.file_uploader("Envie um arquivo .zip contendo o arquivo .ESTABELE", type=["zip"])

add_header = st.checkbox("O arquivo não tem cabeçalho (inserir nomes de colunas manualmente)", value=True)

if "csv_bytes" not in st.session_state:
    st.session_state.csv_bytes = None

if uploaded_file is not None and st.session_state.csv_bytes is None:
    with st.spinner("Processando... isso pode levar alguns minutos."):

        try:
            # Salva o ZIP em arquivo temporário
            with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as temp_zip:
                temp_zip.write(uploaded_file.read())
                temp_zip.flush()

            # Abre o arquivo ZIP a partir do arquivo temporário
            with zipfile.ZipFile(temp_zip.name, 'r') as z:
                arquivos_validos = [name for name in z.namelist() if name.lower().endswith((".estabele", ".csv"))]

                if not arquivos_validos:
                    st.error("O arquivo ZIP não contém arquivos com extensão .ESTABELE ou .csv.")
                else:
                    nome_arquivo = arquivos_validos[0]

                    with z.open(nome_arquivo) as arquivo:
                        reader = pd.read_csv(
                            arquivo,
                            sep=";",
                            encoding="ISO-8859-1",
                            chunksize=100_000,
                            dtype=str,
                            na_filter=False,
                            header=None if add_header else "infer"
                        )

                        with io.BytesIO() as output_buffer:
                            text_buffer = io.TextIOWrapper(output_buffer, encoding="utf-8", write_through=True)

                            progress_bar = st.progress(0)
                            status_text = st.empty()

                            chunk_times = []
                            for i, chunk in enumerate(reader):
                                start_time = time.time()

                                if add_header:
                                    chunk.columns = COLUNAS_ESTABELE

                                chunk.to_csv(text_buffer, index=False, header=(i == 0), sep=";")
                                text_buffer.flush()

                                elapsed = time.time() - start_time
                                chunk_times.append(elapsed)

                                avg_time = sum(chunk_times[-5:]) / min(len(chunk_times), 5)
                                est_time_left = avg_time * 2  # apenas estimativa simbólica

                                progresso = (i + 1) / ((i + 1) + 2)  # aproximação simples
                                progress_bar.progress(min(progresso, 1.0))
                                status_text.info(f"Chunk {i + 1} processado. Estimativa de tempo restante: {est_time_left:.1f} s")

                            st.session_state.csv_bytes = output_buffer.getvalue()

                        st.success(f"Conversão finalizada! Tamanho do arquivo: {len(st.session_state.csv_bytes) / 1e6:.2f} MB")

        except Exception as e:
            st.error(f"Ocorreu um erro ao processar: {str(e)}")

# Exibe o botão de download se o arquivo já foi processado
if st.session_state.csv_bytes:
    st.download_button(
        label="📥 Baixar CSV UTF-8",
        data=st.session_state.csv_bytes,
        file_name="estabelecimentos_convertido.csv",
        mime="text/csv"
    )
