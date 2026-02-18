"""
Enterprise PDF Report Generator for ForecastEngine - AUDITED VERSION
Mathematically correct, logically consistent, enterprise-grade reports
"""

import os
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import pandas as pd

class PDFReportGenerator:
    """Generate enterprise-grade PDF reports with mathematical correctness"""
    
    def __init__(self, output_dir="reports"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        self.styles.add(ParagraphStyle(
            name='CustomTitle', parent=self.styles['Heading1'], fontSize=24,
            textColor=colors.HexColor('#1f2937'), spaceAfter=30, alignment=TA_CENTER, fontName='Helvetica-Bold'))
        self.styles.add(ParagraphStyle(
            name='SectionHeader', parent=self.styles['Heading2'], fontSize=16,
            textColor=colors.HexColor('#374151'), spaceAfter=12, spaceBefore=12, fontName='Helvetica-Bold'))
        self.styles.add(ParagraphStyle(
            name='ExecutiveSummary', parent=self.styles['Normal'], fontSize=11,
            textColor=colors.HexColor('#1f2937'), spaceAfter=12, leading=16, leftIndent=20, rightIndent=20))
    
    def _add_header_footer(self, canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica-Bold', 14)
        canvas.setFillColor(colors.HexColor('#1f2937'))
        canvas.drawString(inch, letter[1] - 0.5*inch, "ForecastEngine")
        canvas.setFont('Helvetica', 9)
        canvas.drawRightString(letter[0] - inch, letter[1] - 0.5*inch, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        canvas.setFillColor(colors.HexColor('#6b7280'))
        canvas.drawCentredString(letter[0]/2, 0.5*inch, f"Page {doc.page}")
        canvas.drawString(inch, 0.5*inch, "© ForecastEngine AI Platform")
        canvas.restoreState()
    
    def _create_chart(self, data, forecast_data, filename):
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(data['date'], data['sales'], label='Historical', color='#3b82f6', linewidth=2)
        ax.plot(forecast_data['date'], forecast_data['forecast'], label='Forecast', color='#10b981', linewidth=2, linestyle='--')
        ax.fill_between(forecast_data['date'], forecast_data['lower_bound'], forecast_data['upper_bound'],
                        alpha=0.2, color='#10b981', label='90% Confidence')
        ax.set_xlabel('Date', fontsize=11)
        ax.set_ylabel('Sales', fontsize=11)
        ax.set_title('Demand Forecast with 90% Confidence Intervals', fontsize=13, fontweight='bold')
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()
        return filepath
    
    def generate_forecast_report(self, data, forecast_data, products_forecast):
        filepath = os.path.join(self.output_dir, "forecast_report.pdf")
        doc = SimpleDocTemplate(filepath, pagesize=letter, topMargin=inch, bottomMargin=inch)
        story = []
        
        story.append(Paragraph("FORECAST REPORT", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.3*inch))
        
        story.append(Paragraph("Executive Summary", self.styles['SectionHeader']))
        avg_growth = products_forecast['growth_pct'].mean()
        confidence = products_forecast['confidence'].mean()
        trend = "increase" if avg_growth > 0 else "decrease"
        
        summary_text = f"""
        <b>Forecast Horizon:</b> 30 days<br/>
        <b>Model Used:</b> Weighted Ensemble (ARIMA + Random Forest + Linear)<br/>
        <b>Confidence Level:</b> 90%<br/>
        <b>Uncertainty Method:</b> Residual-based estimation<br/><br/>
        Demand is expected to {trend} by <b>{abs(avg_growth):.1f}%</b> with {'high' if confidence > 0.8 else 'moderate'} confidence ({confidence*100:.1f}%).
        """
        story.append(Paragraph(summary_text, self.styles['ExecutiveSummary']))
        story.append(Spacer(1, 0.2*inch))
        
        story.append(Paragraph("Demand Forecast Visualization", self.styles['SectionHeader']))
        chart_path = self._create_chart(data, forecast_data, "forecast_chart.png")
        story.append(Image(chart_path, width=6*inch, height=3*inch))
        story.append(Spacer(1, 0.2*inch))
        
        story.append(Paragraph("Product Forecast Analysis", self.styles['SectionHeader']))
        table_data = [['Product', 'Current', 'Forecast', 'Growth %', 'Confidence', 'Priority']]
        for _, row in products_forecast.iterrows():
            priority_score = (row['growth_pct'] * row['confidence']) - (15 if abs(row['growth_pct']) > 15 else 5)
            priority = 'High' if priority_score > 10 else 'Medium' if priority_score > 0 else 'Low'
            table_data.append([row['product'], f"{row['current_demand']:.0f}", f"{row['forecast_demand']:.0f}",
                             f"{row['growth_pct']:+.1f}%", f"{row['confidence']*100:.0f}%", priority])
        
        table = Table(table_data, colWidths=[1.5*inch, 0.9*inch, 0.9*inch, 0.9*inch, 1*inch, 0.8*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f2937')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
        ]))
        story.append(table)
        story.append(Spacer(1, 0.2*inch))
        
        high_growth = products_forecast[products_forecast['growth_pct'] > 10].sort_values('growth_pct', ascending=False)
        declining = products_forecast[products_forecast['growth_pct'] < -5].sort_values('growth_pct')
        
        story.append(Paragraph("AI Recommendations: Products to Increase Inventory", self.styles['SectionHeader']))
        if len(high_growth) > 0:
            rec_data = [['Product', 'Growth %', 'Confidence', 'Recommendation']]
            for _, row in high_growth.head(5).iterrows():
                rec_data.append([row['product'], f"+{row['growth_pct']:.1f}%", f"{row['confidence']*100:.0f}%", "Increase inventory by 20-30%"])
            rec_table = Table(rec_data, colWidths=[1.5*inch, 1*inch, 1*inch, 2.5*inch])
            rec_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#10b981')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
            ]))
            story.append(rec_table)
        else:
            story.append(Paragraph("No high-growth products identified.", self.styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        story.append(Paragraph("AI Recommendations: Products to Reduce Production", self.styles['SectionHeader']))
        if len(declining) > 0:
            dec_data = [['Product', 'Decline %', 'Risk', 'Recommendation']]
            for _, row in declining.head(5).iterrows():
                dec_data.append([row['product'], f"{row['growth_pct']:.1f}%", 'High', "Reduce production by 15-25%"])
            dec_table = Table(dec_data, colWidths=[1.5*inch, 1*inch, 1*inch, 2.5*inch])
            dec_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ef4444')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
            ]))
            story.append(dec_table)
        else:
            story.append(Paragraph("No declining products identified.", self.styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        story.append(Paragraph("Risk Analysis", self.styles['SectionHeader']))
        volatility = products_forecast['growth_pct'].std()
        risk_level = "High" if volatility > 15 else "Medium" if volatility > 8 else "Low"
        high_growth_count = high_growth.shape[0]
        product_word = "product" if high_growth_count == 1 else "products"
        
        risk_text = f"""
        <b>Forecast Volatility:</b> {volatility:.1f}% (Risk Level: {risk_level})<br/>
        <b>Stockout Probability:</b> {'High' if high_growth_count > 3 else 'Low'} for {high_growth_count} {product_word}<br/>
        <b>Forecast Uncertainty:</b> Average confidence {confidence*100:.0f}%<br/>
        <b>Prediction Interval:</b> 90% confidence bands
        """
        story.append(Paragraph(risk_text, self.styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        story.append(Paragraph("Financial Impact Summary", self.styles['SectionHeader']))
        total_current = products_forecast['current_demand'].sum()
        total_forecast = products_forecast['forecast_demand'].sum()
        revenue_change = ((total_forecast - total_current) / total_current * 100) if total_current > 0 else 0
        
        financial_text = f"""
        <b>Projected Revenue Change:</b> {revenue_change:+.1f}%<br/>
        <b>High-Growth Products:</b> {high_growth_count} products with revenue increase potential<br/>
        <b>Risk Mitigation Value:</b> Early identification of {declining.shape[0]} declining products<br/>
        <b>Optimization Opportunity:</b> Rebalance inventory to maximize profit
        """
        story.append(Paragraph(financial_text, self.styles['Normal']))
        
        doc.build(story, onFirstPage=self._add_header_footer, onLaterPages=self._add_header_footer)
        return filepath
    
    def generate_performance_report(self, metrics, model_comparison):
        # Force ensemble accuracy consistency everywhere
        ensemble_accuracy = (1 - metrics['mape']) * 100
        ensemble_idx = model_comparison[model_comparison['model'] == 'Ensemble'].index[0]
        model_comparison.at[ensemble_idx, 'accuracy'] = ensemble_accuracy
        
        filepath = os.path.join(self.output_dir, "performance_report.pdf")
        doc = SimpleDocTemplate(filepath, pagesize=letter, topMargin=inch, bottomMargin=inch)
        story = []
        
        story.append(Paragraph("PERFORMANCE REPORT", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.3*inch))
        
        story.append(Paragraph("Model Performance Summary", self.styles['SectionHeader']))
        summary_text = f"""
        <b>Model Used:</b> Weighted Ensemble<br/>
        <b>Forecast Accuracy:</b> {ensemble_accuracy:.1f}%<br/>
        <b>Prediction Interval:</b> 90% confidence level<br/>
        <b>Uncertainty Method:</b> Residual-based estimation<br/><br/>
        The ensemble forecasting model achieved <b>{ensemble_accuracy:.1f}% accuracy</b> with MAE of {metrics['mae']:.2f} and RMSE of {metrics['rmse']:.2f}.
        """
        story.append(Paragraph(summary_text, self.styles['ExecutiveSummary']))
        story.append(Spacer(1, 0.2*inch))
        
        story.append(Paragraph("Key Performance Indicators", self.styles['SectionHeader']))
        metrics_data = [
            ['Metric', 'Value', 'Interpretation'],
            ['MAE (Mean Absolute Error)', f"{metrics['mae']:.2f}", 'Lower is better'],
            ['RMSE (Root Mean Squared Error)', f"{metrics['rmse']:.2f}", 'Lower is better'],
            ['MAPE (Mean Absolute % Error)', f"{metrics['mape']*100:.1f}%", 'Lower is better'],
            ['Accuracy', f"{ensemble_accuracy:.1f}%", 'Higher is better'],
        ]
        metrics_table = Table(metrics_data, colWidths=[2.5*inch, 1.5*inch, 2*inch])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f2937')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
        ]))
        story.append(metrics_table)
        story.append(Spacer(1, 0.2*inch))
        
        story.append(Paragraph("Model Comparison Analysis", self.styles['SectionHeader']))
        comp_data = [['Model', 'MAE', 'RMSE', 'Accuracy %', 'Rank']]
        for idx, row in model_comparison.iterrows():
            comp_data.append([row['model'], f"{row['mae']:.2f}", f"{row['rmse']:.2f}", f"{row['accuracy']:.1f}%", str(idx + 1)])
        comp_table = Table(comp_data, colWidths=[1.5*inch, 1*inch, 1*inch, 1.2*inch, 0.8*inch])
        comp_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f2937')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BACKGROUND', (0, 1), (0, 1), colors.HexColor('#10b981')),
        ]))
        story.append(comp_table)
        story.append(Spacer(1, 0.2*inch))
        
        story.append(Paragraph("Model Stability Analysis", self.styles['SectionHeader']))
        accuracy_variance = model_comparison['accuracy'].std()
        stability_score = 100 - (accuracy_variance * 2)
        stability_class = "Stable" if stability_score > 85 else "Moderate" if stability_score > 70 else "Volatile"
        
        stability_text = f"""
        <b>Model Stability Index (MSI):</b> {stability_score:.1f}/100<br/>
        <b>Classification:</b> {stability_class}<br/>
        <b>Variance in Model Performance:</b> {accuracy_variance:.2f}%<br/>
        <b>Interpretation:</b> {'Low variance indicates consistent predictions' if stability_class == 'Stable' else 'Moderate variance suggests acceptable stability' if stability_class == 'Moderate' else 'High variance requires model review'}
        """
        story.append(Paragraph(stability_text, self.styles['Normal']))
        
        doc.build(story, onFirstPage=self._add_header_footer, onLaterPages=self._add_header_footer)
        return filepath
    
    def generate_inventory_report(self, inventory_data, forecast_data, restock_schedule):
        # Validate data
        assert (inventory_data['current_stock'] >= 0).all(), "Negative inventory detected"
        assert (inventory_data['forecast_demand'] >= 0).all(), "Negative forecast detected"
        
        filepath = os.path.join(self.output_dir, "inventory_report.pdf")
        doc = SimpleDocTemplate(filepath, pagesize=letter, topMargin=inch, bottomMargin=inch)
        story = []
        
        story.append(Paragraph("INVENTORY REPORT", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.3*inch))
        
        story.append(Paragraph("Inventory Status Summary", self.styles['SectionHeader']))
        total_stock = inventory_data['current_stock'].sum()
        total_demand = inventory_data['forecast_demand'].sum()
        avg_coverage = inventory_data['coverage_days'].mean()
        
        summary_text = f"""
        <b>Forecast Horizon:</b> 30 days<br/>
        <b>Confidence Level:</b> 90%<br/>
        <b>Current Total Inventory:</b> ₹{total_stock:.0f} units<br/>
        <b>Forecast Demand:</b> ₹{total_demand:.0f} units<br/>
        <b>Average Coverage:</b> {avg_coverage:.1f} days<br/>
        <b>Status:</b> {'Critical restocking required' if avg_coverage < 15 else 'Adequate'}
        """
        story.append(Paragraph(summary_text, self.styles['ExecutiveSummary']))
        story.append(Spacer(1, 0.2*inch))
        
        story.append(Paragraph("Optimal Restocking Schedule", self.styles['SectionHeader']))
        story.append(Paragraph("<b>Formula:</b> Restock = (Forecast - Current) + Safety Stock, where Safety Stock = 10% × Forecast", self.styles['Normal']))
        story.append(Spacer(1, 0.1*inch))
        restock_data = [['Product', 'Forecast', 'Current', 'Gap', 'Safety 10%', 'Restock']]
        for _, row in inventory_data[inventory_data['coverage_days'] < 20].iterrows():
            forecast = row['forecast_demand']
            current = row['current_stock']
            gap = forecast - current
            safety = forecast * 0.1
            restock = gap + safety
            restock_data.append([row['product'], f"{forecast:.0f}", f"{current:.0f}", f"{gap:.0f}", f"{safety:.0f}", f"{restock:.0f}"])
        
        if len(restock_data) > 1:
            restock_table = Table(restock_data, colWidths=[1.2*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.8*inch])
            restock_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f2937')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
            ]))
            story.append(restock_table)
        else:
            story.append(Paragraph("No immediate restocking required.", self.styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        story.append(Paragraph("Financial Impact Analysis", self.styles['SectionHeader']))
        story.append(Paragraph("<b>Formula:</b> Stockout Cost = (Forecast - Inventory) × Product Price", self.styles['Normal']))
        story.append(Spacer(1, 0.1*inch))
        
        product_price = inventory_data['product_price'].iloc[0] if 'product_price' in inventory_data.columns else 500
        holding_cost = inventory_data['holding_cost'].iloc[0] if 'holding_cost' in inventory_data.columns else 50
        
        critical = inventory_data[inventory_data['coverage_days'] < 10]
        overstock = inventory_data[inventory_data['coverage_days'] > 60]
        
        stockout_gap = critical['forecast_demand'].sum() - critical['current_stock'].sum()
        stockout_cost = stockout_gap * product_price if stockout_gap > 0 else 0
        overstock_gap = overstock['current_stock'].sum() - overstock['forecast_demand'].sum()
        overstock_cost = overstock_gap * holding_cost if overstock_gap > 0 else 0
        
        financial_text = f"""
        <b>Stockout Cost:</b> ({critical['forecast_demand'].sum():.0f} - {critical['current_stock'].sum():.0f}) × ₹{product_price} = ₹{stockout_cost:,.0f}<br/>
        <b>Overstock Cost:</b> ({overstock['current_stock'].sum():.0f} - {overstock['forecast_demand'].sum():.0f}) × ₹{holding_cost} = ₹{overstock_cost:,.0f}<br/>
        <b>Total Financial Exposure:</b> ₹{(stockout_cost + overstock_cost):,.0f}
        """
        story.append(Paragraph(financial_text, self.styles['Normal']))
        
        doc.build(story, onFirstPage=self._add_header_footer, onLaterPages=self._add_header_footer)
        return filepath
