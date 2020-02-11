# MathML Core Explainer

## Authors:

 * Frédéric Wang
 * Brian Kardell

## Draft specification:

[MathML Core - W3C Editor's Draft](https://mathml-refresh.github.io/mathml-core/)

## Abstract
**[MathML Core](https://mathml-refresh.github.io/mathml-core/)** is a definition of a fundamental subset of features described in the [current MathML 3 recommendation](https://www.w3.org/TR/MathML3/). It attempts to resolve several problems created by MathMLs origins, history and complex status, and properly define its integration in the modern Web Platform in rigorous ways.  The specific subset is derived based on what is widely developed, deployed, proven and used in practice. 
  
## Table of Contents
  * [Goals](#goals)
  * [Non-Goals](#non-goals)
  * [Background: MathML](#background-mathml)
     * [Basic example...](#basic-example)
     * [What is MathML-Core?](#what-is-mathml-core)
        * [The elements of MathML-Core](#the-elements-of-mathml-core)
  * [Design Discussion](#design-discussion)
     * [Not reinventing the wheel](#not-reinventing-the-wheel)
     * [Applying Extensible Web principles](#applying-extensible-web-principles)
  * [Considered Alternatives](#considered-alternatives)
     * [Leave math reliant on SVGs and/or JavaScript libraries](#leave-math-reliant-on-svgs-andor-javascript-libraries)
     * [Abandon MathML in favor some new thing](#abandon-mathml-in-favor-some-new-thing)
        * [Why a tree is good...](#why-a-tree-is-good)
        * [Building atop...](#building-atop)
     * [Focus instead solely on lacking primitives](#focus-instead-solely-on-lacking-primitives)
     * [Enhance MathML3 but keep all or most features](#enhance-mathml3-but-keep-all-or-most-features)
  * [Stakeholder Feedback](#stakeholder-feedback)

  

## Goals 

* To **provide users with efficient, natural, readable and high-quality rendering of mathematical notations**, consistent with other text they encounter in the browser.

* To **provide authors with native, efficient and interoperable rendering of mathematical notations** that they are able to reason about in a manner consistent with the rest of the Web Platform.

* To **rigorously define the necessary subset, how it works and properly integrates into the Web Platform** and ensure testable and interoperable implementations.

* To **establish a productive and agreeable starting point** for additional work and conversation going forward and make it possible to more easily explore more, consistent with the rest of the platform.

## Non-Goals

* To **provide a self-contained solution to problems ultimately better explored through another area of the platform**.
  MathML Core relies as much as possible on existing Web Platform
  features and provides a platform-aligned starting point to solve more
  problems. Examples include, but are not limited to:
  - Specific elements or attributes for styling which
    are better described by existing or new CSS features.
  - Complete and explicit description of semantics which are better
    described by extending ARIA.
  - Open-ended elements to allow implementation-specific features
    instead of standard techniques for customizations and extensions.
  - Native support for editing, interaction, exploration, simple input
      syntax or other advanced features that are better handled by
      DOM/JavaScript and math libraries.
  - Complex graphical layout which can instead be
    performed by embedding MathML in HTML/CSS or SVG.

    *Figure 2: Formulas in a commutative diagram.*

    [![Commutative diagram for the 'first isomorphism theorem'](resources/commutative-diagram.png)](https://en.wikipedia.org/wiki/Commutative_diagram)

* To **fully explain mathematical rendering via as-yet-to-be-defined low-level
  primitives**.
  Rather, these serve as inputs to their possible definition and provide
  valuable insight into needs.

## Background: MathML 

* MathML is the standard developed at the W3C in the mid/late-1990's XML/XHTML era.

* It received much attention and has created a vibrant ecosystem of implementations and integration _outside_ of web browsers  

* CSS, the DOM, the way we write specifications or prove support and interoperability was considerably under-defined.  As a result, the MathML specifications contain several co-evolutionary overlapping approaches better solved elsewhere in the modern platform and lack important levels of detail.

* MathML was supported via a plugin in early IE, it was integrated into the HTML / Parser specifications by WHATWG in the mid-2000's. All HTML compliant parsers _parse_ MathML specially whether they support anything to do with rendering or not.  All browsers (until now) present these uniquely in DOM as simply "Element".  MathML was thus explicitly disadvantaged.

* It was implemented in Firefox about the same time. It gained an implementation in Webkit shortly before the blink split, when it was removed due to complexity and early issues requiring significant attention while Chrome engineers were trying to rework the engine.

* Spec-work continued, without implementation.  As a result, it contains much that is theoretical, including over 150 elements.

### Basic example...

The `<math>` element provides a standard for authors to express and work with text containing generalized relationships about mathematics, in a way very similar to how `<table>` does for expressing text containing relationships about tabular data.


```
<math>
  <mfrac>
    <msup>
      <mi>x</mi>
      <msqrt>
        <mn>5</mn>
      </msqrt>
     </msup>
    <mrow>
      <mi>α</mi>
      <mo>×</mo>
      <mn>7</mn>
    </mrow>
  </mfrac>  
</math>
```

*Figure 1: MathML/DOM for the above 

![Visual MathML rendering as nested boxes representing the DOM tree, with corresponding tag name annotated for each box.](resources/mathml-tree.png)

### What is MathML-Core?

MathML Core is an attempt to create a minimal version of MathML that is well aligned with the modern web platform. It aims to resolve long-standing issues with the split evolution of philosophies between MathML specifications and the larger web platform and create a well-defined starting point based on what is currently widely implemented and increase testability and interoperability.  


####   The elements of MathML-Core  

MathML 3 contained [195 elements](https://www.w3.org/TR/MathML/appendixi.html#index.elem).  MathML-Core focuses on just 32.  Several of these elements exist in deprecated form and simply exist to map the elements and their attributes to newer concepts (let them explain the actual magic) in much the same way `font` remains.  It provides a recommended UA stylesheet for implementation, and adds a couple of new Math oriented display types.

Here is a brief rundown of what those elements _are_...

* the `math` element itself
* 3 elements called `semantics`, `annotation` and `annotation-xml` which simply provide other annotations or potential semantics in existing content but are generally not rendered.
* 6 token elements - "Token elements in presentation markup are broadly intended to represent the smallest units of mathematical notation which carry meaning. Tokens are roughly analogous to words in text. However, because of the precise, symbolic nature of mathematical notation, the various categories and properties of token elements figure prominently in MathML markup. By contrast, in textual data, individual words rarely need to be marked up or styled specially." These are 	(`mtext`, `mi` (identifier), `mn` (number), `mo` (operators in a broad sense), `mspace`, `ms` (string literal - for things like computer algebra systems)
* Layout/Relationship elements `mrow`(for grouping sub-expressions), `mfrac` (for fractions and fraction-like objects such as binomial coefficients and Legendre symbols), `msqrt` and `mroot` for radicals
* `mstyle` (legacy compat, deprecated - just maps to css)
* `merror` (legacy compat - displays its contents as an ”error message”. The intent of this element is to provide a standard way for programs that generate MathML from other input to report syntax errors in their input.)
* `mpadded` - a row-like grouping container which has attributes that map to CSS
* `mphantom` - a co-evolutionary/legacy row-like container that just adds a UA style that maps to visibility: hidden;
* `menclose` - a row-like element for various types of 'enclosure' renderings (see examples at  https://developer.mozilla.org/en-US/docs/Web/MathML/Element/menclose)
* 3 elements about subscripts and superscripts `msub`, `msup` and `msubsup`
* 3 elements about underscripts and overscripts `munder`, `mover` and `munderover`
* 1 element about prescripts and tensor indexes (`mmultiscripts`)`
* 3 elements about tabular math (`mtable`, `mtr` and `mtd`)


## Design Discussion

### Not reinventing the wheel

* As explained in the introduction, MathML is already integrated into
  numerous standards and shipped in two Web engines.
  Consequently, **a new format to replace MathML would be a drastic
  change of direction** and a source of backward compatibility and
  interoperability issues.

* For a native mathematical rendering to be possible, it
  **must adhere to modern browser designs** and a significant effort is being
  made to ensure that MathML Core achieves that goal. For example, all browsers
  use internal tree structures, follow CSS invariants or try to keep code
  size minimal to facilitate security, maintenance, testing, etc

* One **must not duplicate existing Web Platform features**.
  As explained in the non-goals section, MathML Core tries to rely as much as
  possible on existing Web Platform concepts from HTML5 or CSS to describe
  its implementation. Non-fundamental mathematical features that can be
  easily replaced with polyfills or extensions are removed.

* Rendering of mathematical formulas **follow well-established
  rendering rules from TeX and OpenType** which are integrated into MathML
  Core.
  A naive box layout would be enough to get interoperable rendering but is
  likely to
  lead to poor spacing, placement or text rendering inside mathematical
  formulas.

  *Figure 3: Top: Chrome 23 using MathML3 rules and internal heuristics ; Bottom: Igalia's Chromium build using only MathML Core rules.*

  ![Screenshot of MathML in Chrome 23 and Igalia's Chromium build, showing the visual improvements when following MathML Core instead of MathML3.](resources/mathml3-vs-core.png)

### Applying Extensible Web principles

The biggest design decisions centered on how to apply Extensible Web principles
in our own work, as MathML sits in a very unique place in history, and how it
"fits" into the platform.  Not only does it have **existing implementations,
very wide adoption and expectations and integration through the
HTML parser**, but we are approaching it while standards
that in the future might theoretically expose the magic for mathematical
layout, such as
**the CSS Layout API and related Houdini standards, are still developing and significantly in flux**.

In order to balance all of this we decided on the following:

* **Normalize the DOM**.  Because of when and how it was defined, MathML in all
  browsers was exposed to the DOM (in all browsers, through the parser) as
  simply `Element`.  MathML is historically uniquely disadvantaged in this way.  All elements in HTML descend from `HTMLElement` or are `HTMLUnknownElement`.  All elements, even SVG define, some common surface (through a mixin which was called `HTMLOrSVGElement`).  Without remedy, this means that MathML elements lack over 100 bits of API surface.  They have no `.style` property, but are stylable with CSS, for example.  This is unpredictable and confusing for authors who come to MathML and fundamentally limiting for the application of any real Extensible Web ideas.  Aligning the IDL for MathML with the rest of the platform, however, allows that all of our principles and separations (for example ARIA, AOM, Houdini, etc) can move forward in tandem.

* **Acknowledge that some minimal math magic exists in the platform already in two browsers**.
  Our goal then is to not simply block a final implementations of high-level features but to apply Extensible Web principles reasonably and pragmaticaly: Keep it minimal and carefully develop what serves as useful input to the ultimate definition of lower level Houdini APIs.

* **Increase compatibility with CSS**. We provide a design
  compatible with CSS layout and describe how CSS properties are interpreted,
  so that authors can reliably use them to customize math layout.

* Where possible, **attempt to expose information to authors** which would be
  necessary in polyfilling, libraries or extending the platform through platform
  consistent mechanisms.

*Figure 4: Example of using CSS, JavaScript or the Layout API to enhance MathML Core with user-defined features.*

```html
<style>
  math {
     font-family: STIX Two Math;
     color: blue;
  }
  mfrac {
     border: 1px solid dotted;
     padding: 1em;
  }
  .myFancyMathLayout {
     display: layout(myFancyMathLayout);
  }
</style>
<math>
  <mfrac>
    <mrow class="myFancyScriptedElement">
        ...
    </mrow>
    <mrow onclick="myInteractiveAction()">
        ...
    </mrow>
  </mfrac>
</math>
```

## Considered Alternatives

### Leave math reliant on SVGs and/or JavaScript libraries

Writing systems define how we share information. **[Mathematical notations](https://en.wikipedia.org/wiki/Mathematical_notation)
form a fundamental aspect of writing systems.** Math is text, and it is a _normal part_ of text:  Mathematical notations are found in all civilizations.  They have been instrumental throughout history for the diffusion and development of
scientific and technical knowledge. The need for browsers to natively render this kind of text was evident from the
[earliest days of the Web at CERN](https://www.w3.org/MarkUp/HTMLPlus/htmlplus_45.html).  We believe that according to 
the [W3C TAG's Ethical Web Principles](https://www.w3.org/2001/tag/doc/ethical-web-principles/) it is not good for either the Web, the directly impacted communities of authors, or ultimately society to specially disadvantage such an important aspect of communication.

### Abandon MathML in favor some new thing

There are numerous criticisms of MathML.  Like all aspects of the existing
platform, for example, **more succinct forms of expression exist that many
authors are more comfortable writing** (e.g. linear text syntax used in LaTeX or
[Computer algebra systems](https://en.wikipedia.org/wiki/Computer_algebra_system)).
Like other aspects of the platform, it is also possible to be **more semantic
than MathML currently provides**.

A few things don't change though and among them is the difficulty in rendering
interoperable mathematical formulas with good quality.
**Abandoning MathML would be a rejection of an entire ecosystem and decades of
work in standardization and advancement** with little hope that any of the
current state would change in any reasonable timeframe.
This would be tragic as we don't generally require that authors use complex
libraries in order to layout text, or recommend that they be inserted as images.
We believe that **getting native math rendering
is the right thing to do** and that a tree is good.


#### Why a tree is good...
Trees of text relationships aren't the most succinct or easy to type ways to express things. However, this is true of all HTML too.  That's why a lot of HTML is generated from simpler forms like markdown or tools like rich text editors or templating.  A rich ecosystem of tooling has been developed over many years for generating and editing MathML too.

But expressing the content is only part of the challenge and the platform is heavily oriented toward solving these problems via just such a tree. Many benefits flow naturally from simply matching the platform here and expressing mathematics as a standard tree of relationships:

* Browser implementations can natively handle their rendering, as text, efficiently and fluidly.
* Authors can style individual aspects of the equation, for example for educational purposes.
* Authors can ensure that their text, colors, etc match and scale appropriately
* Authors can create interactivity with those elements or manipulate them (educational purposes are a good example here too)
* Software can be used to derive more meaning from context in much the same way that search engines do (there are in fact, applications that do this)
* We are granted common, platform-fitting places to attach additional semantics through existing mechanisms.
* 'Find' text works

#### Building atop...
Given these abilities and approach, building atop additional semantics, extensions, conversions and further
explorations** becomes very plausible.  It is even entirely plausible to support shorthand expansion from forms like LaTeX or ASCII Math, in much the same we can for Markdown. Patterns for extending shorthand notations like these are a common class of problem that should be well explored and, still, probably rendered into a Shadow tree natively if ever supported natively.

*Figure 5: LaTeX source in a [custom element](https://fred-wang.github.io/TeXZilla/examples/customElement.html) rendered using MathML in a shadow DOM, with the [Latin Modern Math font](http://www.gust.org.pl/projects/e-foundry/lm-math) ; From top to bottom: Blink (Igalia's build), WebKit (r249360) and Gecko (Firefox 68)*

```html
<la-tex>
  {\Gamma(t)}
  = {\int_{0}^{+\infty} x^{t-1} e^{-x} dx}
  = {\frac{1}{t}
     \prod_{n=1}^\infty
     \frac{\left(1+\frac{1}{n}\right)^t}{1+\frac{t}{n}}}
  \sim {\sqrt{\frac{2\pi}{t}} \left(\frac{t}{e}\right)^t}
</la-tex>
```
![Screenshot of a MathML formula in different browsers.](resources/mathml-example-gamma.png)

### Focus instead solely on lacking primitives

A big part of the challenge of focusing on lacking primitives is that
**it leaves open the question of what is lacking**.  The main proposals here of
things to focus on have to do with additional semantics, 'stretchy characters'
and complex alignments.  While we agree that these are all excellent goals, we
believe that they are also very independently pursuable, and that both causes
are boosted by doing so.

However, without also providing a detailed
layout specification, pursuing native rendering in all browsers or
performing interoperability
tests it becomes very **hard to design a full browser-compatible math rendering
implementation and to introduce necessary web platform
primitives**. Thus we again relegate
ourselves to the current state of one of the hardest problems in a way that we
don't for other forms of text.

### Enhance MathML3 but keep all or most features

Another approach would be to integrate the TeX/OpenType and HTML5/CSS
improvements but at the same time preserving all or most features from MathML3.
We discarded this approach for several reasons:

* **Some MathML3 features don't integrate well within the web platform**
  and it is not clear how to keep them and at the same time try to align MathML
  with browser design. **Other features duplicate existing web platform
  primitives without re-using them**.
  As explained in section "Not reinventing the wheel", these are strong blockers
  to get new features accepted. Indeed, many of these have never been
  implemented in browsers or have been removed.

* **Some MathML3 features have very low or almost null usage**.
  This means it is very
  difficult to justify effort for implementing them natively and maintaining
  them while the rest of the codebase evolves.
  Instead, we prefer to focus on a small subset that is used in practice, and
  in agreement with Extensible Web principles, add the necessary APIs to let
  users build extension on top of MathML Core.

* **MathML3 has many features, is underspecified, lacks automated tests and is
  only partially implemented in browsers**. This means that keeping all the
  features and at the same time achieving interoperability would require a huge
  effort. Again, the choice was instead to consider a subset of manageable size,
  corresponding to what is used on web pages and implemented in two WebKit and
  Gecko.
## Stakeholder Feedback

* ...
* ...
* ...
