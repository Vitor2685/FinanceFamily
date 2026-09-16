from flask import Flask, render_template, request, redirect, url_for, send_file
from database import (
    criar_banco,
    obter_renda,
    atualizar_renda,
    adicionar_gasto,
    obter_gastos,
    excluir_gasto,
    obter_total_gastos
)

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)

from pathlib import Path
from datetime import datetime


app = Flask(__name__)

criar_banco()


@app.route("/")
def index():

    renda = obter_renda()
    gastos = obter_gastos()
    total = obter_total_gastos()
    saldo = renda - total

    return render_template(
        "index.html",
        renda=renda,
        gastos=gastos,
        total=total,
        saldo=saldo
    )


@app.route("/renda", methods=["POST"])
def salvar_renda():

    renda = request.form.get("renda", "0")

    try:
        renda = float(renda.replace(",", "."))
    except ValueError:
        renda = 0

    atualizar_renda(renda)

    return redirect(url_for("index"))


@app.route("/adicionar", methods=["POST"])
def adicionar():

    descricao = request.form.get("descricao")
    categoria = request.form.get("categoria")
    valor = request.form.get("valor")
    data = request.form.get("data")

    try:
        valor = float(valor.replace(",", "."))
    except (ValueError, AttributeError):
        valor = 0

    if descricao and categoria and valor > 0 and data:
        adicionar_gasto(
            descricao,
            categoria,
            valor,
            data
        )

    return redirect(url_for("index"))


@app.route("/excluir/<int:gasto_id>")
def excluir(gasto_id):

    excluir_gasto(gasto_id)

    return redirect(url_for("index"))


@app.route("/pdf")
def gerar_pdf():

    renda = obter_renda()
    gastos = obter_gastos()
    total = obter_total_gastos()
    saldo = renda - total

    pasta_relatorios = Path("relatorios")
    pasta_relatorios.mkdir(exist_ok=True)

    arquivo = pasta_relatorios / "relatorio_gastos.pdf"

    documento = SimpleDocTemplate(
        str(arquivo),
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    estilos = getSampleStyleSheet()

    titulo = estilos["Title"]
    titulo.alignment = TA_CENTER

    elementos = []

    elementos.append(
        Paragraph(
            "RELATÓRIO DE GASTOS MENSAIS",
            titulo
        )
    )

    elementos.append(Spacer(1, 20))

    data_atual = datetime.now().strftime("%d/%m/%Y")

    elementos.append(
        Paragraph(
            f"Relatório gerado em: {data_atual}",
            estilos["Normal"]
        )
    )

    elementos.append(Spacer(1, 20))

    resumo = [
        ["RESUMO FINANCEIRO", "VALOR"],
        ["Renda mensal", f"R$ {renda:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")],
        ["Total de gastos", f"R$ {total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")],
        ["Saldo", f"R$ {saldo:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")]
    ]

    tabela_resumo = Table(resumo, colWidths=[300, 150])

    tabela_resumo.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
            ("TOPPADDING", (0, 0), (-1, 0), 10),
        ])
    )

    elementos.append(tabela_resumo)

    elementos.append(Spacer(1, 30))

    elementos.append(
        Paragraph(
            "DETALHAMENTO DOS GASTOS",
            estilos["Heading2"]
        )
    )

    elementos.append(Spacer(1, 10))

    dados = [
        ["Data", "Descrição", "Categoria", "Valor"]
    ]

    for gasto in gastos:

        valor_formatado = (
            f"R$ {gasto['valor']:,.2f}"
            .replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
        )

        dados.append([
            gasto["data"],
            gasto["descricao"],
            gasto["categoria"],
            valor_formatado
        ])

    if len(dados) == 1:
        dados.append([
            "-",
            "Nenhum gasto cadastrado",
            "-",
            "R$ 0,00"
        ])

    tabela_gastos = Table(
        dados,
        colWidths=[70, 180, 100, 80],
        repeatRows=1
    )

    tabela_gastos.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (-1, 1), (-1, -1), "RIGHT"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
            ("TOPPADDING", (0, 0), (-1, 0), 8),
        ])
    )

    elementos.append(tabela_gastos)

    elementos.append(Spacer(1, 25))

    elementos.append(
        Paragraph(
            "Este relatório foi gerado automaticamente pelo Controle Financeiro.",
            estilos["Normal"]
        )
    )

    documento.build(elementos)

    return send_file(
        arquivo,
        as_attachment=True,
        download_name="relatorio_gastos.pdf"
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)