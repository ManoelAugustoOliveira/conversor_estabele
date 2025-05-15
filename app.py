import streamlit as st
import pandas as pd
import zipfile
import io

# Lista de colunas padrão (para aplicar nomes se necessário)
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

if uploaded_file is not None:
    with st.spinner("Processando... isso pode levar alguns minutos."):
        try:
            with zipfile.ZipFile(uploaded_file) as z:
                # Busca arquivos .ESTABELE ou .csv no ZIP
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

                            for i, chunk in enumerate(reader):
                                if add_header:
                                    chunk.columns = COLUNAS_ESTABELE
                                chunk.to_csv(text_buffer, index=False, header=(i == 0), sep=";")

                            text_buffer.flush()
                            csv_bytes = output_buffer.getvalue()

                        st.success(f"Conversão finalizada! Tamanho do arquivo: {len(csv_bytes) / 1e6:.2f} MB")

                        st.download_button(
                            label="📥 Baixar CSV UTF-8",
                            data=csv_bytes,
                            file_name="estabelecimentos_convertido.csv",
                            mime="text/csv"
                        )

        except Exception as e:
            st.error(f"Ocorreu um erro ao processar: {str(e)}")
