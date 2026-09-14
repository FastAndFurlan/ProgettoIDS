from flask import Flask, render_template, request
import pandas as pd
app = Flask(__name__)
df = pd.read_csv('Referendum_1946_2026.csv', sep=';', encoding='utf-8-sig')
df = df.loc[:, ~df.columns.str.startswith('Unnamed')]

for col in ['ELETTORI', 'VOTANTI', 'NUMVOTISI', 'NUMVOTINO', 'SCHEDE_BIANCHE']:
    df[col] = pd.to_numeric(df[col], errors='coerce')


@app.route('/')
def home():
    anni = sorted(df['ANNO'].unique().tolist())
    regioni = sorted(df['REGIONE'].unique().tolist())
    province_per_regione = (
        df[['REGIONE', 'PROVINCIA']]
        .drop_duplicates()
        .groupby('REGIONE')['PROVINCIA']
        .apply(lambda x: sorted(x.tolist()))
        .to_dict()
    )
    tipi_referendum = sorted(df['TIPO_REFERENDUM'].dropna().unique().tolist())
    ambiti_referendum = sorted(df['AMBITO_REFERENDUM'].dropna().unique().tolist())

    # Filtri scelti dall'utente (arrivano nell'URL grazie a method="get" nel form)
    anno_sel = request.args.get('anno', '')
    regione_sel = request.args.get('regione', '')
    provincia_sel = request.args.get('provincia', '')
    tipo_sel = request.args.get('argomento', '')
    ambito_sel = request.args.get('ambito', '')

    filtrato = df.copy()
    if anno_sel:
        filtrato = filtrato[filtrato['ANNO'] == int(anno_sel)]
    if regione_sel:
        filtrato = filtrato[filtrato['REGIONE'] == regione_sel]
    if provincia_sel:
        filtrato = filtrato[filtrato['PROVINCIA'] == provincia_sel]
    if tipo_sel:
        filtrato = filtrato[filtrato['TIPO_REFERENDUM'] == tipo_sel]
    if ambito_sel:
        filtrato = filtrato[filtrato['AMBITO_REFERENDUM'] == ambito_sel]
    chiavi = ['ANNO', 'ANNO_SPECIFICO', 'NUM_REFERENDUM', 'QUESITO', 'TIPO_REFERENDUM', 'AMBITO_REFERENDUM']
    if provincia_sel:
        chiavi.append('PROVINCIA')
    elif regione_sel:
        chiavi.append('REGIONE')

    risultati = (
        filtrato.groupby(chiavi, as_index=False)
        .agg(
            elettori=('ELETTORI', 'sum'),
            votanti=('VOTANTI', 'sum'),
            voti_si=('NUMVOTISI', 'sum'),
            voti_no=('NUMVOTINO', 'sum'),
        )
    )

    risultati['affluenza_pct'] = (risultati['votanti'] / risultati['elettori'] * 100).round(2)
    risultati['quorum_raggiunto'] = risultati.apply(
        lambda r: ('Sì' if r['affluenza_pct'] >= 50 else 'No') if r['TIPO_REFERENDUM'] == 'Abrogativo' else 'Non previsto',
        axis=1,
    )
    risultati['esito'] = risultati.apply(lambda r: 'Sì' if r['voti_si'] > r['voti_no'] else 'No', axis=1)
    risultati = risultati.sort_values(['ANNO', 'NUM_REFERENDUM'])

    # --- Andamento affluenza nel tempo, sugli stessi dati filtrati ---
    andamento = (
        risultati.groupby('ANNO', as_index=False)
        .agg(elettori=('elettori', 'sum'), votanti=('votanti', 'sum'))
    )
    andamento['affluenza_pct'] = (andamento['votanti'] / andamento['elettori'] * 100).round(2)
    andamento = andamento.sort_values('ANNO')

    # --- Riepilogo per ambito, sugli stessi dati filtrati ---
    riepilogo_ambito = []
    for ambito, gruppo in risultati.groupby('AMBITO_REFERENDUM'):
        affluenza_media = (gruppo['votanti'].sum() / gruppo['elettori'].sum() * 100)
        solo_abrogativi = gruppo[gruppo['TIPO_REFERENDUM'] == 'Abrogativo']
        if len(solo_abrogativi) > 0:
            pct_quorum = (solo_abrogativi['affluenza_pct'] >= 50).mean() * 100
        else:
            pct_quorum = None  # nessun abrogativo in questo ambito con questi filtri
        riepilogo_ambito.append({
            'ambito': ambito,
            'n_referendum': len(gruppo),
            'affluenza_media': round(affluenza_media, 2),
            'pct_quorum_raggiunto': round(pct_quorum, 1) if pct_quorum is not None else None,
        })
    riepilogo_ambito = sorted(riepilogo_ambito, key=lambda r: r['affluenza_media'], reverse=True)

    # --- Grafico geografico: ha senso solo con un anno fissato e più di una zona da confrontare ---
    grafico_geografico = pd.DataFrame()
    mostra_grafico_geografico = False
    if anno_sel and not provincia_sel:
        if regione_sel:
            # anno + regione fissati -> confronto tra le province di quella regione
            base = (
                filtrato.groupby('PROVINCIA', as_index=False)
                .agg(elettori=('ELETTORI', 'sum'), votanti=('VOTANTI', 'sum'))
            )
            etichetta_geografica = 'PROVINCIA'
        else:
            # solo anno fissato -> confronto tra tutte le regioni
            base = (
                filtrato.groupby('REGIONE', as_index=False)
                .agg(elettori=('ELETTORI', 'sum'), votanti=('VOTANTI', 'sum'))
            )
            etichetta_geografica = 'REGIONE'

        base['affluenza_pct'] = (base['votanti'] / base['elettori'] * 100).round(2)
        base = base.sort_values('affluenza_pct', ascending=False)
        grafico_geografico = base.rename(columns={etichetta_geografica: 'nome'})
        mostra_grafico_geografico = len(grafico_geografico) > 1

    # --- Grafico quesiti: ha senso solo se ci sono più quesiti nella stessa giornata di voto ---
    grafico_quesiti = (
        risultati[['QUESITO', 'affluenza_pct']]
        .drop_duplicates(subset='QUESITO')
        .to_dict(orient='records')
    )
    mostra_grafico_quesiti = anno_sel != '' and len(grafico_quesiti) > 1

    # --- Il grafico ad andamento ha senso solo se ci sono più anni da confrontare ---
    mostra_grafico = andamento['ANNO'].nunique() > 1

    # Un solo return, alla fine, con tutto quello che serve al template
    return render_template(
        'index.html',
        anni=anni,
        regioni=regioni,
        province_per_regione=province_per_regione,
        tipi_referendum=tipi_referendum,
        ambiti_referendum=ambiti_referendum,
        risultati=risultati.to_dict(orient='records'),
        filtri={'anno': anno_sel, 'regione': regione_sel, 'provincia': provincia_sel,
                'argomento': tipo_sel, 'ambito': ambito_sel},
        andamento=andamento.to_dict(orient='records'),
        mostra_grafico=mostra_grafico,
        grafico_geografico=grafico_geografico.to_dict(orient='records') if len(grafico_geografico) > 0 else [],
        mostra_grafico_geografico=mostra_grafico_geografico,
        grafico_quesiti=grafico_quesiti,
        mostra_grafico_quesiti=mostra_grafico_quesiti,
        riepilogo_ambito=riepilogo_ambito,
    )
@app.route('/idee')#reindirizzamento a pagina nuove idee
def idee():
    return render_template('nuoveIdee.html')
@app.route('/homePage')#reindirizzamento a home page
def homePage():
    return home()
if __name__ == '__main__':
    app.run(debug=True)