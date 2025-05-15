import streamlit as st
import pandas as pd
import zipfile
import io

# Lista de colunas padrão (para opção de aplicar nomes)
COLUNAS_ESTABELE = [
    'CNPJ_BASICO', 'CNPJ_ORDEM', 'CNPJ_DV', 'IDENTIFICADOR_MATRIZ_FILIAL',
    'NOME_FANTASIA', 'SITUACAO_CADASTRAL', 'DATA_SITUACAO_CADASTRAL',
    'MOTIVO_SITUACAO_CADASTRAL', 'NOME_CIDADE_EXTERIOR', 'PAIS',
    'DATA_INICIO_ATIVIDADE', 'CNAE_FISCAL_PRINCIPAL', 'CNAE_FISCAL_SECUNDARIA',
    'TIPO_LOGRADOURO', 'LOGRADOURO', 'NUMERO', 'COMPLEMENTO', 'BAIRRO', 'CEP',
    'UF', 'MUNICIPIO', 'DDD1', 'TELEFONE1', 'DDD2', 'TELEFONE2', 'DDD_FAX',
    'FAX', 'EMAIL', 'SITUACAO_ESPECIAL', 'DATA_SITUACAO_ESPECIAL'
]

st.title("Conversor de CSV para UTF-8 (Streamlit Cloud-friendly)")

uploaded_file = st.file_uploader("Envie um arquivo .zip contendo o CSV", type=["zip"])

add_header = st.checkbox("O CSV não tem cabeçalho (inserir nomes de coluna automaticamente)", value=False)

if uploaded_file is not None:
    with st.spinner("Processando... isso pode levar alguns minutos."):

        try:
            with zipfile.ZipFile(uploaded_file) as z:
                csv_names = [name for name in z.namelist() if name.lower().endswith(".csv")]

                if not csv_names:
                    st.error("O arquivo ZIP não contém nenhum CSV.")
                else:
                    csv_name = csv_names[0]
                    with z.open(csv_name) as csv_file:
                        # Leitura em blocos
                        reader = pd.read_csv(
                            csv_file,
                            encoding="ISO-8859-1",
                            chunksize=100_000,
                            dtype=str,
                            na_filter=False,
                            header=None if add_header else "infer"
                        )

                        output_buffer = io.BytesIO()
                        text_buffer = io.TextIOWrapper(output_buffer, encoding="utf-8", write_through=True)

                        for i, chunk in enumerate(reader):
                            if add_header:
                                chunk.columns = COLUNAS_ESTABELE
                            chunk.to_csv(text_buffer, index=False, header=(i == 0))

                        text_buffer.flush()
                        text_buffer.close()
                        csv_bytes = output_buffer.getvalue()

                        st.success(f"Conversão concluída com sucesso! Tamanho final: {len(csv_bytes) / 1e6:.2f} MB")

                        st.download_button(
                            "📥 Baixar CSV otimizado",
                            data=csv_bytes,
                            file_name="estabelecimentos_convertido.csv",
                            mime="text/csv"
                        )

        except Exception as e:
            st.error(f"Ocorreu um erro: {str(e)}")
