# Builder UX

Source refs: ../event-form-prd.md, ../tech-architecture.md

## Canvas and Layouts
- Canvas aspect: 16:9 default; responsive preview targets: mobile, tablet, desktop
- Layout grid: 8px base grid; snapping increments: 8px; toggleable grid/snapping
- Layers: z-order managed via properties panel; object locking supported

## Properties Panel
- Common properties: position (x,y), size (w,h), z-index, visibility
- Field-specific: placeholder/label/help, required, validation, options (for selects)

## Snapping & Preview Guarantees
- Snaps to grid and object edges; keyboard nudge by 1px, with Shift for 8px
- Preview mode is read-only and uses the same render path as publish

## Tab Order Rules
- Auto-order by top-to-bottom, left-to-right; manual override per object

## Accessibility Defaults
- Labels associated via `for`/`id`
- Keyboard focus visible; ARIA roles for interactive elements



