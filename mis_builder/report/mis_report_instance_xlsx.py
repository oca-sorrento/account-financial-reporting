# -*- coding: utf-8 -*-
# © 2014-2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from collections import defaultdict
import logging

from openerp.report import report_sxw

from ..models.accounting_none import AccountingNone

_logger = logging.getLogger(__name__)

try:
    from openerp.addons.report_xlsx.report.report_xlsx import ReportXlsx
except ImportError:
    _logger.debug("report_xslx not installed, Excel export non functional")

    class ReportXslx:
        pass


ROW_HEIGHT = 15  # xlsxwriter units
COL_WIDTH = 0.9  # xlsxwriter units
MIN_COL_WIDTH = 10  # characters
MAX_COL_WIDTH = 50  # characters


class MisBuilderXslx(ReportXlsx):

    def __init__(self, name, table, rml=False, parser=False, header=True,
                 store=False):
        super(MisBuilderXslx, self).__init__(
            name, table, rml, parser, header, store)

    def make_number_format(self, kpi, comparison=False):
        # TODO FIXME comparison
        number_format = '#'
        if kpi.dp:
            number_format += '.'
            number_format += '0' * kpi.dp
        # TODO FIXME factor
        if kpi.prefix:
            number_format = u'"{} "{}'.format(kpi.prefix, number_format)
        if kpi.suffix:
            number_format = u'{}" {}"'.format(number_format, kpi.suffix)
        return number_format

    def generate_xlsx_report(self, workbook, data, objects):

        # get the computed result of the report
        matrix = objects._compute_matrix()

        # create worksheet
        report_name = '{} - {}'.format(
            objects[0].name, objects[0].company_id.name)
        sheet = workbook.add_worksheet(report_name[:31])
        row_pos = 0
        col_pos = 0
        # width of the labels column
        label_col_width = MIN_COL_WIDTH
        # {col_pos: max width in characters}
        col_width = defaultdict(lambda: MIN_COL_WIDTH)

        # document title
        bold = workbook.add_format({'bold': True})
        header_format = workbook.add_format({
            'bold': True, 'align': 'center', 'bg_color': '#F0EEEE'})
        sheet.write(row_pos, 0, report_name, bold)
        row_pos += 2

        # column headers
        sheet.write(row_pos, 0, '', header_format)
        col_pos = 1
        for col in matrix.iter_cols():
            label = col.description
            if col.comment:
                label += '\n' + col.comment
                sheet.set_row(row_pos, ROW_HEIGHT * 2)
            if col.colspan > 1:
                sheet.merge_range(
                    row_pos, col_pos, row_pos,
                    col_pos + col.colspan-1,
                    label, header_format)
            else:
                sheet.write(row_pos, col_pos, label, header_format)
                col_width[col_pos] = max(col_width[col_pos],
                                         len(col.description or ''),
                                         len(col.comment or ''))
            col_pos += col.colspan
        row_pos += 1

        # sub column headers
        sheet.write(row_pos, 0, '', header_format)
        col_pos = 1
        for subcol in matrix.iter_subcols():
            label = subcol.description
            if subcol.comment:
                label += '\n' + subcol.comment
                sheet.set_row(row_pos, ROW_HEIGHT * 2)
            sheet.write(row_pos, col_pos, label, header_format)
            col_width[col_pos] = max(col_width[col_pos],
                                     len(subcol.description or ''),
                                     len(subcol.comment or ''))
            col_pos += 1
        row_pos += 1

        # rows
        for row in matrix.iter_rows():
            if row.style:
                row_xlsx_style = row.style.to_xlsx_format_properties()
            else:
                row_xlsx_style = {}
            row_format = workbook.add_format(row_xlsx_style)
            col_pos = 0
            sheet.write(row_pos, col_pos, row.description, row_format)
            label_col_width = max(label_col_width, len(row.description or ''))
            for cell in row.iter_cells():
                col_pos += 1
                if not cell or cell.val is AccountingNone:
                    sheet.write(row_pos, col_pos, '', row_format)
                    continue
                kpi_xlsx_style = dict(row_xlsx_style)
                kpi_xlsx_style.update({
                    'num_format': self.make_number_format(row.kpi),
                    'align': 'right'
                })
                kpi_format = workbook.add_format(kpi_xlsx_style)
                # TODO FIXME kpi computed style
                # TODO FIXME pct in comparision columns
                val = cell.val
                if row.kpi.type == 'pct':
                    val = val / 0.01
                sheet.write(row_pos, col_pos, val, kpi_format)
                col_width[col_pos] = max(col_width[col_pos],
                                         len(cell.val_rendered or ''))
            row_pos += 1

        # adjust col widths
        sheet.set_column(0, 0, min(label_col_width, MAX_COL_WIDTH) * COL_WIDTH)
        data_col_width = min(MAX_COL_WIDTH, max(*col_width.values()))
        min_col_pos = min(*col_width.keys())
        max_col_pos = max(*col_width.keys())
        sheet.set_column(min_col_pos, max_col_pos, data_col_width * COL_WIDTH)


MisBuilderXslx('report.mis.report.instance.xlsx',
               'mis.report.instance', parser=report_sxw.rml_parse)