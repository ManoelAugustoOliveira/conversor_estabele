import streamlit as st
import pandas as pd

COLUNAS_ESTABELE = [
    'CNPJ_BASICO', 'CNPJ_ORDEM', 'CNPJ_DV', 'IDENTIFICADOR_MATRIZ_FILIAL',
    'NOME_FANTASIA', 'SITUACAO_CADASTRAL', 'DATA_SITUACAO_CADASTRAL',
    'MOTIVO_SITUACAO_CADASTRAL', 'NOME_CIDADE_EXTERIOR', 'PAIS',
    'DATA_INICIO_ATIVIDADE', 'CNAE_FISCAL_PRINCIPAL', 'CNAE_FISCAL_SECUNDARIA',
    'TIPO_LOGRADOURO', 'LOGRADOURO', 'NUMERO', 'COMPLEMENTO', 'BAIRRO', 'CEP',
    'UF', 'MUNICIPIO', 'DDD1', 'TELEFONE1', 'DDD2', 'TELEFONE2', 'DDD_FAX',
    'FAX', 'EMAIL', 'SITUACAO_ESPECIAL', 'DATA_SITUACAO_ESPECIAL'
]

def ler_estabele(file) -> pd.DataFrame:
    return pd.read_csv(
        file,
        sep=';',
        names=COLUNAS_ESTABELE,
        header=None,
        encoding='latin1',
        dtype=str
    )

def main():
    st.set_page_config(page_title="Conversor ESTABELE", layout="wide")
    st.title("📄 Conversor de Arquivo ESTABELE (Receita Federal) para CSV")
    st.write(
        "Faça upload de um arquivo `.ESTABELE` delimitado por ponto e vírgula (`;`) e baixe a versão convertida para CSV."
    )

    uploaded_file = st.file_uploader("Selecione o arquivo .ESTABELE", type=["txt", "ESTABELE", "csv"])

    if uploaded_file:
        try:
            df = ler_estabele(uploaded_file)
            st.success(f"Arquivo carregado com sucesso! Total de registros: {len(df):,}")

            st.subheader("Prévia dos dados:")
            st.dataframe(df.head(20), use_container_width=True)

            csv_bytes = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Baixar como CSV",
                data=csv_bytes,
                file_name="estabele_convertido.csv",
                mime="text/csv"
            )
        except Exception as e:
            st.error(f"Ocorreu um erro ao processar o arquivo: {e}")

if __name__ == "__main__":
    main()
