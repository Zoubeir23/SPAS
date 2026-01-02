import jsPDF from 'jspdf'
import autoTable from 'jspdf-autotable'
import * as XLSX from 'xlsx'

/**
 * Interface pour les colonnes d'un tableau
 */
export interface ExportColumn {
  key: string
  label: string
  format?: (value: any) => string
}

/**
 * Exporte un tableau de données vers un fichier PDF
 */
export function exportToPDF(
  data: any[],
  columns: ExportColumn[],
  filename: string,
  title?: string
): void {
  const doc = new jsPDF()
  
  // Ajouter le titre si fourni
  if (title) {
    doc.setFontSize(18)
    doc.text(title, 14, 20)
  }

  // Préparer les données pour autoTable
  const tableData = data.map((row) =>
    columns.map((col) => {
      const value = row[col.key]
      return col.format ? col.format(value) : value?.toString() || ''
    })
  )

  const tableHeaders = columns.map((col) => col.label)

  // Générer le tableau
  autoTable(doc, {
    head: [tableHeaders],
    body: tableData,
    startY: title ? 30 : 20,
    styles: { fontSize: 9 },
    headStyles: { fillColor: [28, 65, 166] }, // Couleur primary
    alternateRowStyles: { fillColor: [245, 247, 250] },
  })

  // Sauvegarder le PDF
  doc.save(`${filename}.pdf`)
}

/**
 * Exporte un tableau de données vers un fichier Excel
 */
export function exportToExcel(
  data: any[],
  columns: ExportColumn[],
  filename: string,
  sheetName: string = 'Données'
): void {
  // Préparer les données
  const worksheetData = [
    columns.map((col) => col.label), // En-têtes
    ...data.map((row) =>
      columns.map((col) => {
        const value = row[col.key]
        return col.format ? col.format(value) : value?.toString() || ''
      })
    ),
  ]

  // Créer le workbook et la worksheet
  const workbook = XLSX.utils.book_new()
  const worksheet = XLSX.utils.aoa_to_sheet(worksheetData)

  // Ajuster la largeur des colonnes
  const colWidths = columns.map(() => ({ wch: 20 }))
  worksheet['!cols'] = colWidths

  // Ajouter la worksheet au workbook
  XLSX.utils.book_append_sheet(workbook, worksheet, sheetName)

  // Sauvegarder le fichier
  XLSX.writeFile(workbook, `${filename}.xlsx`)
}

/**
 * Exporte un dashboard complet vers PDF
 */
export function exportDashboardToPDF(
  dashboardData: {
    title: string
    kpis?: Array<{ label: string; value: string | number }>
    tables?: Array<{ title: string; data: any[]; columns: ExportColumn[] }>
    charts?: Array<{ title: string; description: string }>
  },
  filename: string
): void {
  const doc = new jsPDF()
  let yPosition = 20

  // Titre principal
  doc.setFontSize(20)
  doc.setFont('helvetica', 'bold')
  doc.text(dashboardData.title, 14, yPosition)
  yPosition += 15

  // Date de génération
  doc.setFontSize(10)
  doc.setFont('helvetica', 'normal')
  doc.text(
    `Généré le ${new Date().toLocaleDateString('fr-FR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })}`,
    14,
    yPosition
  )
  yPosition += 15

  // KPIs
  if (dashboardData.kpis && dashboardData.kpis.length > 0) {
    doc.setFontSize(14)
    doc.setFont('helvetica', 'bold')
    doc.text('Indicateurs Clés de Performance', 14, yPosition)
    yPosition += 10

    doc.setFontSize(10)
    doc.setFont('helvetica', 'normal')
    const kpiData = dashboardData.kpis.map((kpi) => [kpi.label, String(kpi.value)])

    autoTable(doc, {
      head: [['Indicateur', 'Valeur']],
      body: kpiData,
      startY: yPosition,
      styles: { fontSize: 10 },
      headStyles: { fillColor: [28, 65, 166] },
    })

    yPosition = (doc as any).lastAutoTable.finalY + 15
  }

  // Tableaux
  if (dashboardData.tables && dashboardData.tables.length > 0) {
    dashboardData.tables.forEach((table, _index) => {
      // Nouvelle page si nécessaire
      if (yPosition > 250) {
        doc.addPage()
        yPosition = 20
      }

      doc.setFontSize(14)
      doc.setFont('helvetica', 'bold')
      doc.text(table.title, 14, yPosition)
      yPosition += 10

      const tableData = table.data.map((row) =>
        table.columns.map((col) => {
          const value = row[col.key]
          return col.format ? col.format(value) : value?.toString() || ''
        })
      )

      const tableHeaders = table.columns.map((col) => col.label)

      autoTable(doc, {
        head: [tableHeaders],
        body: tableData,
        startY: yPosition,
        styles: { fontSize: 9 },
        headStyles: { fillColor: [28, 65, 166] },
        alternateRowStyles: { fillColor: [245, 247, 250] },
      })

      yPosition = (doc as any).lastAutoTable.finalY + 15
    })
  }

  // Graphiques (description seulement)
  if (dashboardData.charts && dashboardData.charts.length > 0) {
    if (yPosition > 250) {
      doc.addPage()
      yPosition = 20
    }

    doc.setFontSize(14)
    doc.setFont('helvetica', 'bold')
    doc.text('Graphiques', 14, yPosition)
    yPosition += 10

    doc.setFontSize(10)
    doc.setFont('helvetica', 'normal')
    dashboardData.charts.forEach((chart) => {
      doc.text(chart.title, 14, yPosition)
      yPosition += 7
      doc.text(chart.description, 14, yPosition)
      yPosition += 10
    })
  }

  // Sauvegarder
  doc.save(`${filename}.pdf`)
}

