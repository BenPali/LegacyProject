# Accessibilité & Recommandations Handicap (WCAG 2.1 AA)

## Objectif
Garantir que l'application et la documentation sont utilisables par tous, y compris les personnes en situation de handicap.

## Standards
- WCAG 2.1 niveau AA
- RGAA (référence FR), ARIA pour sémantique

## Exigences clés
- Contrastes: ratio ≥ 4.5:1 (texte normal)
- Clavier: navigation complète sans souris, focus visible
- Lecteurs d'écran: libellés explicites, ordre DOM logique
- Médias: alternatives textuelles, sous-titres si vidéo
- Animations: évitables, respect de `prefers-reduced-motion`

## Bonnes pratiques dev
- Composants avec rôles ARIA, labels et `aria-describedby`
- Titres hiérarchisés (h1…h6), liens explicites
- État et erreurs annoncés (aria-live)
- Formulaires: labels associés, champs requis indiqués

## Vérification
- Outils: axe DevTools, Lighthouse, pa11y-ci
- Tests manuels: navigation clavier, lecteur d'écran (NVDA/VoiceOver)

## Plan d'intégration
- Critères d'acceptation accessibilité sur stories UI
- Audit à chaque jalon majeur
- Défauts classés et suivis en backlog


