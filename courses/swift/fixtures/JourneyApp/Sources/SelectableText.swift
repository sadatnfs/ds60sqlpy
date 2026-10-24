import SwiftUI

#if canImport(UIKit)
  import UIKit

  struct SelectableText: UIViewRepresentable {
    let text: String
    func makeUIView(context: Context) -> UITextView {
      let view = UITextView()
      view.isEditable = false
      view.isScrollEnabled = false
      view.adjustsFontForContentSizeCategory = true
      view.font = .preferredFont(forTextStyle: .body)
      view.backgroundColor = .clear
      return view
    }
    func updateUIView(_ view: UITextView, context: Context) {
      if view.text != text { view.text = text }
    }
  }
#elseif canImport(AppKit)
  import AppKit

  struct SelectableText: NSViewRepresentable {
    let text: String
    func makeNSView(context: Context) -> NSTextField {
      let view = NSTextField(wrappingLabelWithString: text)
      view.isSelectable = true
      return view
    }
    func updateNSView(_ view: NSTextField, context: Context) {
      if view.stringValue != text { view.stringValue = text }
    }
  }
#endif
