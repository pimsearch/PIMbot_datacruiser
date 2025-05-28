from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename
from functools import lru_cache
from itertools import zip_longest
import tempfile
import pandas as pd
import os
import re

app = Flask(__name__)

UPLOAD_FOLDER = os.path.join(tempfile.gettempdir(), "data_cruiser_uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def limpar_caracteres_invalidos_excel(df):
    def limpar_valor(v):
        if isinstance(v, str):
            return re.sub(r"[\x00-\x1F\x7F-\x9F]", "", v)
        return v
    cols = df.columns[df.dtypes == 'object']
    for col in cols:
        df[col] = df[col].map(limpar_valor)
    return df


@lru_cache(maxsize=None)
def col_letter_to_index(letter):
    letter = letter.upper()
    index = 0
    for char in letter:
        index = index * 26 + (ord(char) - ord('A') + 1)
    return index - 1


def load_dataframe(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    try:
        if ext == ".csv":
            return pd.read_csv(file_path, sep=";", encoding="utf-8")
        elif ext in [".xlsx", ".xls"]:
            return pd.read_excel(file_path, sheet_name=0)
        elif ext == ".xlsb":
            import pyxlsb
            return pd.read_excel(file_path, engine="pyxlsb", sheet_name=0)
        else:
            raise ValueError(f"Formato não suportado: {ext}")
    except Exception as e:
        raise ValueError(f"Erro ao abrir o arquivo {file_path}: {str(e)}")

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file1 = request.files["file1"]
        file2 = request.files["file2"]
        col1 = request.form["col1"]
        col2 = request.form["col2"]
        col_val = request.form["col_val"]

        filename1 = os.path.join(UPLOAD_FOLDER, secure_filename(file1.filename))
        filename2 = os.path.join(UPLOAD_FOLDER, secure_filename(file2.filename))
        file1.save(filename1)
        file2.save(filename2)

        df1 = load_dataframe(filename1)
        df2 = load_dataframe(filename2)

        idx1 = col_letter_to_index(col1)
        idx2 = col_letter_to_index(col2)
        idx_val = col_letter_to_index(col_val)

        col1_name = df1.columns[idx1]
        col2_name = df2.columns[idx2]
        col_val_name = df2.columns[idx_val]

        # Agrupa e transforma em colunas extras, mas limitando o máximo por performance
        LIMIT = 10  # até 10 colunas por item (ajustável)
        agrupado = (
            df2.groupby(col2_name)[col_val_name]
            .apply(lambda x: list(x)[:LIMIT])
            .reset_index()
        )

        colunas_extras = [f"{col_val_name}_{i+1}" for i in range(LIMIT)]
        valores_expandido = [list(v[:LIMIT]) + [None] * (LIMIT - len(v)) for v in agrupado[col_val_name]]

        agrupado_df = pd.DataFrame(valores_expandido, columns=colunas_extras)

        # Garante que a coluna de chave está na primeira posição sem duplicar
        if col2_name not in agrupado_df.columns:
            agrupado_df.insert(0, col2_name, agrupado[col2_name])
        else:
            agrupado_df[col2_name] = agrupado[col2_name]
            agrupado_df = agrupado_df[[col2_name] + [c for c in agrupado_df.columns if c != col2_name]]

        # Converte os campos de chave para string antes do merge
        df1[col1_name] = df1[col1_name].astype(str)
        agrupado_df[col2_name] = agrupado_df[col2_name].astype(str)

        # Merge agora usando colunas expandidas
        merged_df = df1.merge(agrupado_df, how='left', left_on=col1_name, right_on=col2_name)


        output_path = os.path.join(UPLOAD_FOLDER, "resultado.xlsx")
        merged_df = limpar_caracteres_invalidos_excel(merged_df)

        if len(merged_df) > 300_000:
            output_path = os.path.join(UPLOAD_FOLDER, "resultado.csv")
            merged_df.to_csv(output_path, index=False, sep=";")
            mimetype = "text/csv"
        else:
            merged_df.to_excel(output_path, index=False)
            mimetype = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

        return send_file(
            output_path,
            as_attachment=True,
            download_name=os.path.basename(output_path),
            mimetype=mimetype
        )

    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)