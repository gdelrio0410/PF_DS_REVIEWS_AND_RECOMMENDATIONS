def filtrar_dataframe(dataframe, columna, frase):
    nuevo_dataframe = dataframe[dataframe[columna].str.contains(frase)]
    return nuevo_dataframe


def Estado_Rest(data,estado):
    df=data[data['Estado'] == estado]
    df=pd.DataFrame(df)
    df=sns.countplot(y='category', data=df, order=df['category'].value_counts().head(5).index)
    return df


def valorUnico(df, columna):
    valores_unicos = df[columna].unique()
    print(valores_unicos)


def verificarTipoDato(df):
    for columna_nombre in df.columns:
        tipo_dato = type(df[columna_nombre][0])
        primer_elemento = df[columna_nombre][0]
        
        print(f"La columna '{columna_nombre}' es de tipo de dato: {tipo_dato}")
        print(f"contenido: {primer_elemento}")
        print()

def transformar_cadena(cadena):
    import ast
    try:
        return ast.literal_eval(cadena)
    except (ValueError, SyntaxError):
        return cadena