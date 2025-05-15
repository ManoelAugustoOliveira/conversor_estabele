import streamlit as st
import pandas as pd
import io

COLUNAS_ESTABELE = [
    'CNPJ_BASICO', 'CNPJ_ORDEM', 'CNPJ_DV', 'IDENTIFICADOR_MATRIZ_FILIAL',
    'NOME_FANTASIA', 'SITUACAO_CADASTRAL', 'DATA_SITUACAO_CADASTRAL',
    'MOTIVO_SITUACAO_CADASTRAL', 'NOME_CIDADE_EXTERIOR', 'PAIS',
    'DATA_INICIO_ATIVIDADE', 'CNAE_FISCAL_PRINCIPAL', 'CNAE_FISCAL_SECUNDARIA',
    'TIPO_LOGRADOURO', 'LOGRADOURO', 'NUMERO', 'COMPLEMENTO', 'BAIRRO', 'CEP',
    'UF', 'MUNICIPIO', 'DDD1', 'TELEFONE1', 'DDD2', 'TELEFONE2', 'DDD_FAX',
    'FAX', 'EMAIL', 'SITUACAO_ESPECIAL', 'DATA_SITUACAO_ESPECIAL'
]

st.title("Conversor de Arquivo Estabelecimentos CNPJ")

uploaded_file = st.file_uploader("Selecione o arquivo bruto (.ESTABELE)", type=["ESTABELE", "txt", "csv"])

if uploaded_file:
    st.info("Lendo arquivo... isso pode levar alguns minutos para arquivos grandes.")

    try:
        # Leitura em blocos para eficiência
        chunk_size = 500_000
        reader = pd.read_csv(
            uploaded_file,
            sep=';',
            names=COLUNAS_ESTABELE,
            header=None,
            encoding='latin1',
            dtype=str,
            chunksize=chunk_size,
        )

        buffer = io.StringIO()
        for i, chunk in enumerate(reader):
            chunk.to_csv(buffer, index=False, encoding='utf-8', header=(i == 0))  # Só escreve o header na primeira vez

        buffer.seek(0)
        st.success("Conversão concluída!")

        st.download_button(
            label="📥 Baixar CSV otimizado",
            data=buffer.getvalue(),
            file_name="estabelecimentos_convertido.csv",
            mime="text/csv"
        )

    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {str(e)}")
