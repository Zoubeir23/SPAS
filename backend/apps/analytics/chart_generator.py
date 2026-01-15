"""
Chart Generator Service
Génère des graphiques avec matplotlib et plotly pour le dashboard.
"""
import io
import base64
from typing import List, Dict, Any, Optional
from datetime import datetime
import matplotlib
matplotlib.use('Agg')  # Backend non-interactif pour serveur
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from plotly.io import to_image
import pandas as pd


class ChartGenerator:
    """Service pour générer des graphiques avec Python."""
    
    @staticmethod
    def generate_line_chart(
        data: List[Dict[str, Any]],
        x_key: str = 'name',
        y_key: str = 'value',
        title: str = '',
        x_label: str = '',
        y_label: str = '',
        width: int = 800,
        height: int = 400,
        format: str = 'png'
    ) -> bytes:
        """
        Génère un graphique en ligne (évolution).
        
        Args:
            data: Liste de dictionnaires avec les données
            x_key: Clé pour l'axe X
            y_key: Clé pour l'axe Y
            title: Titre du graphique
            x_label: Label de l'axe X
            y_label: Label de l'axe Y
            width: Largeur en pixels
            height: Hauteur en pixels
            format: Format de sortie ('png', 'svg', 'jpg')
        
        Returns:
            Bytes de l'image générée
        """
        if not data:
            # Graphique vide si pas de données
            fig = go.Figure()
            fig.add_annotation(
                text="Aucune donnée disponible",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
        else:
            df = pd.DataFrame(data)
            fig = px.line(
                df,
                x=x_key,
                y=y_key,
                title=title,
                labels={x_key: x_label or x_key, y_key: y_label or y_key},
                markers=True
            )
            
            fig.update_layout(
                width=width,
                height=height,
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(size=12),
                title_font_size=16,
                xaxis=dict(gridcolor='#e2e8f0'),
                yaxis=dict(gridcolor='#e2e8f0'),
            )
        
        # Convertir en image
        if format == 'png':
            return to_image(fig, format='png', width=width, height=height)
        elif format == 'svg':
            return to_image(fig, format='svg', width=width, height=height)
        else:
            return to_image(fig, format='jpeg', width=width, height=height)
    
    @staticmethod
    def generate_pie_chart(
        data: List[Dict[str, Any]],
        name_key: str = 'name',
        value_key: str = 'value',
        title: str = '',
        width: int = 600,
        height: int = 400,
        format: str = 'png'
    ) -> bytes:
        """
        Génère un graphique circulaire (camembert).
        
        Args:
            data: Liste de dictionnaires avec les données
            name_key: Clé pour les noms
            value_key: Clé pour les valeurs
            title: Titre du graphique
            width: Largeur en pixels
            height: Hauteur en pixels
            format: Format de sortie ('png', 'svg', 'jpg')
        
        Returns:
            Bytes de l'image générée
        """
        if not data:
            # Graphique vide si pas de données
            fig = go.Figure()
            fig.add_annotation(
                text="Aucune donnée disponible",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
        else:
            df = pd.DataFrame(data)
            fig = px.pie(
                df,
                names=name_key,
                values=value_key,
                title=title,
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            
            fig.update_traces(
                textposition='inside',
                textinfo='percent+label',
                hovertemplate='<b>%{label}</b><br>Valeur: %{value}<br>Pourcentage: %{percent}<extra></extra>'
            )
            
            fig.update_layout(
                width=width,
                height=height,
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(size=12),
                title_font_size=16,
                showlegend=True,
                legend=dict(
                    orientation="v",
                    yanchor="middle",
                    y=0.5,
                    xanchor="left",
                    x=1.05
                )
            )
        
        # Convertir en image
        if format == 'png':
            return to_image(fig, format='png', width=width, height=height)
        elif format == 'svg':
            return to_image(fig, format='svg', width=width, height=height)
        else:
            return to_image(fig, format='jpeg', width=width, height=height)
    
    @staticmethod
    def generate_bar_chart(
        data: List[Dict[str, Any]],
        x_key: str = 'name',
        y_key: str = 'value',
        title: str = '',
        x_label: str = '',
        y_label: str = '',
        width: int = 800,
        height: int = 400,
        format: str = 'png'
    ) -> bytes:
        """
        Génère un graphique en barres.
        
        Args:
            data: Liste de dictionnaires avec les données
            x_key: Clé pour l'axe X
            y_key: Clé pour l'axe Y
            title: Titre du graphique
            x_label: Label de l'axe X
            y_label: Label de l'axe Y
            width: Largeur en pixels
            height: Hauteur en pixels
            format: Format de sortie ('png', 'svg', 'jpg')
        
        Returns:
            Bytes de l'image générée
        """
        if not data:
            fig = go.Figure()
            fig.add_annotation(
                text="Aucune donnée disponible",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
        else:
            df = pd.DataFrame(data)
            fig = px.bar(
                df,
                x=x_key,
                y=y_key,
                title=title,
                labels={x_key: x_label or x_key, y_key: y_label or y_key},
                color=y_key,
                color_continuous_scale='Blues'
            )
            
            fig.update_layout(
                width=width,
                height=height,
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(size=12),
                title_font_size=16,
                xaxis=dict(gridcolor='#e2e8f0'),
                yaxis=dict(gridcolor='#e2e8f0'),
            )
        
        if format == 'png':
            return to_image(fig, format='png', width=width, height=height)
        elif format == 'svg':
            return to_image(fig, format='svg', width=width, height=height)
        else:
            return to_image(fig, format='jpeg', width=width, height=height)

